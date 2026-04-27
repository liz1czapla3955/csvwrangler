"""Type-coerce columns based on inferred or explicit type mappings."""
import csv
import io
from typing import Dict, Iterable, Iterator, List, Optional


_TRUTHY = {"true", "yes", "1", "on"}
_FALSY = {"false", "no", "0", "off"}


def _coerce(value: str, dtype: str) -> str:
    """Coerce *value* to *dtype*, returning original string on failure."""
    if dtype == "int":
        try:
            return str(int(float(value)))
        except (ValueError, TypeError):
            return value
    if dtype == "float":
        try:
            return str(float(value))
        except (ValueError, TypeError):
            return value
    if dtype == "bool":
        low = value.strip().lower()
        if low in _TRUTHY:
            return "true"
        if low in _FALSY:
            return "false"
        return value
    if dtype == "str":
        return value.strip()
    return value


def retype_rows(
    rows: Iterable[Dict[str, str]],
    types: Dict[str, str],
) -> Iterator[Dict[str, str]]:
    """Yield rows with specified columns coerced to the given types.

    Parameters
    ----------
    rows:
        Iterable of dicts representing CSV rows.
    types:
        Mapping of column name -> target type ("int", "float", "bool", "str").
    """
    for row in rows:
        out = dict(row)
        for col, dtype in types.items():
            if col in out:
                out[col] = _coerce(out[col], dtype)
        yield out


def retype_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    types: Dict[str, str],
) -> None:
    """Read *reader*, coerce column types, and write to *writer*."""
    writer.writeheader()
    for row in retype_rows(reader, types):
        writer.writerow(row)
