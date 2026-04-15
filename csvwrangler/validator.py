"""CSV column validation against simple schema rules."""

import csv
import io
from typing import Any, Dict, List, Optional, Tuple


VALID_TYPES = {"integer", "float", "boolean", "date", "string"}
BOOLEAN_TRUE = {"true", "yes", "1"}
BOOLEAN_FALSE = {"false", "no", "0"}


def _check_value(value: str, expected_type: str) -> bool:
    """Return True if value matches the expected type."""
    if value == "":
        return True  # treat empty as always valid (nullable)
    if expected_type == "integer":
        try:
            int(value)
            return True
        except ValueError:
            return False
    if expected_type == "float":
        try:
            float(value)
            return True
        except ValueError:
            return False
    if expected_type == "boolean":
        return value.strip().lower() in BOOLEAN_TRUE | BOOLEAN_FALSE
    if expected_type == "date":
        import re
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", value.strip()))
    return True  # string accepts anything


def validate_rows(
    rows: List[Dict[str, str]],
    rules: Dict[str, str],
    required: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Validate rows against type rules and required columns.

    Returns a list of violation dicts with keys: row, column, value, reason.
    """
    required = required or []
    violations: List[Dict[str, Any]] = []

    for rule_type in rules.values():
        if rule_type not in VALID_TYPES:
            raise ValueError(f"Unknown type in rules: '{rule_type}'. Valid types: {VALID_TYPES}")

    for row_index, row in enumerate(rows, start=1):
        for col in required:
            if not row.get(col, "").strip():
                violations.append({
                    "row": row_index,
                    "column": col,
                    "value": row.get(col, ""),
                    "reason": "required field is empty",
                })
        for col, expected_type in rules.items():
            if col not in row:
                continue
            value = row[col]
            if not _check_value(value, expected_type):
                violations.append({
                    "row": row_index,
                    "column": col,
                    "value": value,
                    "reason": f"expected {expected_type}, got '{value}'",
                })

    return violations


def validate_file(
    input_path: str,
    rules: Dict[str, str],
    required: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Read a CSV file and validate its rows."""
    with open(input_path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return validate_rows(rows, rules, required)
