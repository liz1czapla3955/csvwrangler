import csv
import io
from typing import Iterator


def slice_rows(
    rows: list[dict],
    start: int = 0,
    stop: int | None = None,
    step: int = 1,
) -> list[dict]:
    """Return a slice of rows using start/stop/step semantics."""
    if step == 0:
        raise ValueError("step cannot be zero")
    return rows[start:stop:step]


def slice_file(
    reader: Iterator[dict],
    writer,
    start: int = 0,
    stop: int | None = None,
    step: int = 1,
) -> None:
    """Read all rows, slice them, and write results."""
    rows = list(reader)
    if not rows:
        return
    sliced = slice_rows(rows, start=start, stop=stop, step=step)
    if not sliced:
        writer.writeheader()
        return
    writer.writeheader()
    for row in sliced:
        writer.writerow(row)
