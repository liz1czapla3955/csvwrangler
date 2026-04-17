import csv
import io
from typing import Iterable, Iterator


def pad_rows(
    rows: Iterable[dict],
    columns: list[str],
    width: int,
    fill_char: str = "0",
    align: str = "right",
) -> Iterator[dict]:
    """Pad string values in specified columns to a minimum width."""
    if align not in ("left", "right"):
        raise ValueError(f"align must be 'left' or 'right', got {align!r}")
    if len(fill_char) != 1:
        raise ValueError("fill_char must be exactly one character")
    if width < 1:
        raise ValueError("width must be at least 1")

    for row in rows:
        out = dict(row)
        for col in columns:
            if col not in out:
                continue
            val = out[col]
            if align == "right":
                out[col] = val.rjust(width, fill_char)
            else:
                out[col] = val.ljust(width, fill_char)
        yield out


def pad_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    width: int,
    fill_char: str = "0",
    align: str = "right",
) -> None:
    writer.writeheader()
    for row in pad_rows(reader, columns, width, fill_char, align):
        writer.writerow(row)
