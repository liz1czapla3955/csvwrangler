"""Column and value normalization: strip whitespace, change case, replace characters."""

from __future__ import annotations

import csv
import io
from typing import Dict, Iterable, Iterator, List, Optional


def normalize_headers(
    rows: List[Dict[str, str]],
    case: Optional[str] = None,
    strip: bool = True,
    replace: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """Return rows with header keys normalized.

    Args:
        rows: Input rows as list of dicts.
        case: One of 'lower', 'upper', 'title', or None to leave unchanged.
        strip: Whether to strip leading/trailing whitespace from header names.
        replace: Mapping of substrings to replace in header names.
    """
    if not rows:
        return []

    replace = replace or {}
    original_keys = list(rows[0].keys())

    def _transform(key: str) -> str:
        if strip:
            key = key.strip()
        for old, new in replace.items():
            key = key.replace(old, new)
        if case == "lower":
            key = key.lower()
        elif case == "upper":
            key = key.upper()
        elif case == "title":
            key = key.title()
        return key

    key_map = {k: _transform(k) for k in original_keys}
    return [{key_map[k]: v for k, v in row.items()} for row in rows]


def normalize_values(
    rows: List[Dict[str, str]],
    columns: Optional[List[str]] = None,
    case: Optional[str] = None,
    strip: bool = True,
) -> List[Dict[str, str]]:
    """Return rows with string values normalized.

    Args:
        rows: Input rows as list of dicts.
        columns: Columns to normalize; if None, all columns are processed.
        case: One of 'lower', 'upper', 'title', or None.
        strip: Whether to strip whitespace from values.
    """
    if not rows:
        return []

    target = set(columns) if columns else None

    def _transform(value: str) -> str:
        if strip:
            value = value.strip()
        if case == "lower":
            value = value.lower()
        elif case == "upper":
            value = value.upper()
        elif case == "title":
            value = value.title()
        return value

    result = []
    for row in rows:
        new_row = {
            k: (_transform(v) if (target is None or k in target) else v)
            for k, v in row.items()
        }
        result.append(new_row)
    return result


def normalize_file(
    input_text: str,
    header_case: Optional[str] = None,
    value_case: Optional[str] = None,
    strip: bool = True,
    replace: Optional[Dict[str, str]] = None,
    columns: Optional[List[str]] = None,
) -> str:
    """Read CSV text, normalize headers and/or values, return CSV text."""
    reader = csv.DictReader(io.StringIO(input_text))
    rows = list(reader)
    rows = normalize_headers(rows, case=header_case, strip=strip, replace=replace)
    rows = normalize_values(rows, columns=columns, case=value_case, strip=strip)
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
