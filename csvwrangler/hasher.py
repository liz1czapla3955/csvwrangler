import csv
import hashlib
from typing import Iterable, Iterator


def _hash_value(value: str, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    h.update(value.encode("utf-8"))
    return h.hexdigest()


def hash_rows(
    rows: Iterable[dict],
    columns: list[str],
    algorithm: str = "sha256",
    suffix: str = "_hash",
) -> Iterator[dict]:
    for row in rows:
        out = dict(row)
        for col in columns:
            if col not in row:
                continue
            out[col + suffix] = _hash_value(row[col], algorithm)
        yield out


def hash_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    algorithm: str = "sha256",
    suffix: str = "_hash",
) -> None:
    rows = list(reader)
    if not rows:
        return
    sample = dict(rows[0])
    for col in columns:
        if col in sample:
            sample[col + suffix] = ""
    fieldnames = list(rows[0].keys())
    extra = [c + suffix for c in columns if c in rows[0]]
    writer.fieldnames = fieldnames + extra
    writer.writeheader()
    for row in hash_rows(rows, columns, algorithm, suffix):
        writer.writerow(row)
