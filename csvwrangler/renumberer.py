"""Renumber rows by resetting or continuing a numeric index column."""

import csv
import io
from typing import Iterable, Iterator


def renumber_rows(
    rows: Iterable[dict],
    column: str = "id",
    start: int = 1,
    step: int = 1,
    overwrite: bool = True,
) -> Iterator[dict]:
    """Yield rows with a renumbered index column.

    Args:
        rows: Iterable of row dicts.
        column: Name of the column to write the index into.
        start: Starting value for the counter.
        step: Increment between successive values.
        overwrite: If False and the column already exists with a non-empty
                   value, leave the existing value unchanged.
    """
    counter = start
    for row in rows:
        new_row = dict(row)
        if overwrite or new_row.get(column, "") == "":
            new_row[column] = str(counter)
        counter += step
        yield new_row


def renumber_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str = "id",
    start: int = 1,
    step: int = 1,
    overwrite: bool = True,
) -> None:
    """Read rows from *reader*, renumber, and write to *writer*."""
    fieldnames = list(reader.fieldnames or [])
    if column not in fieldnames:
        fieldnames = [column] + fieldnames

    writer.fieldnames = fieldnames
    writer.writeheader()
    for row in renumber_rows(reader, column=column, start=start, step=step, overwrite=overwrite):
        writer.writerow({f: row.get(f, "") for f in fieldnames})
