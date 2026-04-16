"""Cast CSV column values to specified types."""
import csv
import io
from typing import Iterable, Iterator


SUPPORTED_TYPES = {"int", "float", "str", "bool"}


def _cast_value(value: str, dtype: str) -> str:
    """Cast a string value to dtype and return as string."""
    if dtype == "int":
        return str(int(float(value)))
    elif dtype == "float":
        return str(float(value))
    elif dtype == "bool":
        if value.strip().lower() in ("1", "true", "yes"):
            return "true"
        elif value.strip().lower() in ("0", "false", "no"):
            return "false"
        else:
            raise ValueError(f"Cannot cast {value!r} to bool")
    elif dtype == "str":
        return str(value)
    else:
        raise ValueError(f"Unsupported type: {dtype!r}. Choose from {SUPPORTED_TYPES}")


def cast_rows(
    rows: Iterable[dict],
    casts: dict,
    errors: str = "raise",
) -> Iterator[dict]:
    """Yield rows with specified columns cast to given types.

    Args:
        rows: Iterable of row dicts.
        casts: Mapping of column name to target type string.
        errors: 'raise' to raise on bad cast, 'ignore' to leave value as-is.
    """
    for row in rows:
        new_row = dict(row)
        for col, dtype in casts.items():
            if col not in new_row:
                continue
            try:
                new_row[col] = _cast_value(new_row[col], dtype)
            except (ValueError, TypeError):
                if errors == "raise":
                    raise
        yield new_row


def cast_file(
    input_text: str,
    casts: dict,
    errors: str = "raise",
) -> str:
    """Cast columns in CSV text and return updated CSV text."""
    reader = csv.DictReader(io.StringIO(input_text))
    fieldnames = reader.fieldnames or []
    rows = list(cast_rows(reader, casts, errors=errors))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()
