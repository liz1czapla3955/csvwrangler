"""Schema inference for CSV files."""

import csv
import re
from collections import defaultdict
from typing import Dict, List, Optional

DATE_PATTERNS = [
    re.compile(r'^\d{4}-\d{2}-\d{2}$'),
    re.compile(r'^\d{2}/\d{2}/\d{4}$'),
    re.compile(r'^\d{2}-\d{2}-\d{4}$'),
]


def _infer_type(value: str) -> str:
    """Infer the type of a single string value."""
    if value.strip() == '':
        return 'empty'
    try:
        int(value)
        return 'integer'
    except ValueError:
        pass
    try:
        float(value)
        return 'float'
    except ValueError:
        pass
    if value.lower() in ('true', 'false', 'yes', 'no'):
        return 'boolean'
    for pattern in DATE_PATTERNS:
        if pattern.match(value.strip()):
            return 'date'
    return 'string'


def _resolve_types(types: List[str]) -> str:
    """Resolve a list of observed types into a single inferred type."""
    type_set = set(t for t in types if t != 'empty')
    if not type_set:
        return 'string'
    if len(type_set) == 1:
        return type_set.pop()
    if type_set <= {'integer', 'float'}:
        return 'float'
    return 'string'


def infer_schema(filepath: str, sample_size: int = 100, delimiter: str = ',') -> Dict[str, str]:
    """Infer column types from a CSV file.

    Args:
        filepath: Path to the CSV file.
        sample_size: Number of rows to sample for inference.
        delimiter: CSV delimiter character.

    Returns:
        A dict mapping column name to inferred type.
    """
    observed: Dict[str, List[str]] = defaultdict(list)

    with open(filepath, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        if reader.fieldnames is None:
            return {}
        for i, row in enumerate(reader):
            if i >= sample_size:
                break
            for field, value in row.items():
                observed[field].append(_infer_type(value or ''))

    return {field: _resolve_types(types) for field, types in observed.items()}


def format_schema(schema: Dict[str, str]) -> str:
    """Format a schema dict as a human-readable string."""
    if not schema:
        return '(no columns detected)'
    width = max(len(col) for col in schema)
    lines = [f"{'Column':<{width}}  Type", '-' * (width + 10)]
    for col, dtype in schema.items():
        lines.append(f"{col:<{width}}  {dtype}")
    return '\n'.join(lines)
