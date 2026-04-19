import csv
import io
from typing import Iterator


def limit_rows(
    rows: list[dict],
    limit: int,
    offset: int = 0,
) -> list[dict]:
    """Return up to `limit` rows starting at `offset`."""
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if offset < 0:
        raise ValueError("offset must be non-negative")
    return rows[offset: offset + limit]


def limit_file(
    reader: Iterator[dict],
    writer,
    limit: int,
    offset: int = 0,
) -> None:
    """Stream rows from reader, skip `offset`, write up to `limit` rows."""
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if offset < 0:
        raise ValueError("offset must be non-negative")

    header_written = False
    skipped = 0
    written = 0

    for row in reader:
        if not header_written:
            writer.writeheader()
            header_written = True
        if skipped < offset:
            skipped += 1
            continue
        if written >= limit:
            break
        writer.writerow(row)
        written += 1
