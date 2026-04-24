"""Offset numeric column values by a fixed amount or percentage."""

from typing import Iterator


def _offset_value(value: str, amount: float, percent: bool) -> str:
    """Apply an offset to a single value string.

    Args:
        value: The raw string value from the CSV cell.
        amount: The offset amount (absolute or percentage).
        percent: If True, treat amount as a percentage of the original value.

    Returns:
        The offset value as a string, or the original value if non-numeric.
    """
    stripped = value.strip()
    if stripped == "":
        return value
    try:
        numeric = float(stripped)
    except ValueError:
        return value

    if percent:
        result = numeric + (numeric * amount / 100.0)
    else:
        result = numeric + amount

    # Preserve integer representation when possible
    if result == int(result) and "." not in stripped:
        return str(int(result))
    return str(result)


def offset_rows(
    rows: Iterator[dict],
    columns: list[str],
    amount: float,
    percent: bool = False,
) -> Iterator[dict]:
    """Yield rows with numeric columns shifted by a fixed amount or percentage.

    Args:
        rows: Iterable of row dicts.
        columns: Column names to apply the offset to.
        amount: The offset amount.
        percent: If True, apply as a percentage offset.

    Yields:
        Row dicts with offset values applied.
    """
    for row in rows:
        new_row = dict(row)
        for col in columns:
            if col in new_row:
                new_row[col] = _offset_value(new_row[col], amount, percent)
        yield new_row


def offset_file(
    reader,
    writer,
    columns: list[str],
    amount: float,
    percent: bool = False,
) -> None:
    """Read CSV rows, apply offset, and write results.

    Args:
        reader: A csv.DictReader instance.
        writer: A csv.DictWriter instance.
        columns: Column names to offset.
        amount: The offset amount.
        percent: If True, apply as a percentage offset.
    """
    writer.writeheader()
    for row in offset_rows(reader, columns, amount, percent):
        writer.writerow(row)
