"""Column-level deduplication: remove duplicate values within a column, replacing repeats with empty string."""
import csv
import io
from typing import Iterable, Iterator


def dedup_column_rows(
    rows: Iterable[dict],
    columns: list[str],
) -> Iterator[dict]:
    """Yield rows where repeated consecutive values in *columns* are blanked out."""
    seen: dict[str, str] = {}
    for row in rows:
        out = dict(row)
        for col in columns:
            val = row.get(col, "")
            if col in seen and seen[col] == val:
                out[col] = ""
            else:
                seen[col] = val
        yield out


def dedup_column_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
) -> None:
    """Read from *reader*, blank consecutive duplicate values in *columns*, write to *writer*."""
    writer.writeheader()
    for row in dedup_column_rows(reader, columns):
        writer.writerow(row)
