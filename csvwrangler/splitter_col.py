"""Split a single column into multiple columns by a delimiter."""
import csv
import io
from typing import Iterator


def split_column_rows(
    rows: Iterator[dict],
    column: str,
    delimiter: str = ",",
    output_columns: list[str] | None = None,
    max_split: int = -1,
) -> Iterator[dict]:
    """Split *column* on *delimiter* into new columns.

    If *output_columns* is given, the split parts are mapped to those names.
    If there are fewer parts than output columns the extras are empty strings.
    If *output_columns* is None the parts are named ``{column}_1``, ``{column}_2``, …
    The original column is removed.
    """
    for row in rows:
        value = row.get(column, "")
        if max_split >= 0:
            parts = value.split(delimiter, max_split)
        else:
            parts = value.split(delimiter)

        if output_columns:
            names = output_columns
        else:
            names = [f"{column}_{i + 1}" for i in range(len(parts))]

        new_row = {k: v for k, v in row.items() if k != column}
        for i, name in enumerate(names):
            new_row[name] = parts[i] if i < len(parts) else ""
        yield new_row


def split_column_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    delimiter: str = ",",
    output_columns: list[str] | None = None,
    max_split: int = -1,
) -> None:
    rows = list(reader)
    if not rows:
        return
    result = list(
        split_column_rows(rows, column, delimiter, output_columns, max_split)
    )
    writer.fieldnames = list(result[0].keys()) if result else []
    writer.writeheader()
    for row in result:
        writer.writerow(row)
