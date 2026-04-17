import csv
import io
from collections import Counter
from typing import Iterable, Iterator


def count_values(rows: Iterable[dict], column: str, sort_by: str = "count", ascending: bool = False) -> list[dict]:
    """Count occurrences of each unique value in a column."""
    counter: Counter = Counter()
    for row in rows:
        if column not in row:
            raise KeyError(f"Column '{column}' not found in row")
        counter[row[column]] += 1

    results = [{"value": val, "count": cnt} for val, cnt in counter.items()]

    if sort_by == "count":
        results.sort(key=lambda r: r["count"], reverse=not ascending)
    elif sort_by == "value":
        results.sort(key=lambda r: r["value"], reverse=not ascending)
    else:
        raise ValueError(f"sort_by must be 'count' or 'value', got '{sort_by}'")

    return results


def count_file(reader: csv.DictReader, writer: csv.DictWriter, column: str, sort_by: str = "count", ascending: bool = False) -> None:
    """Read CSV rows, count values in column, write results."""
    rows = list(reader)
    results = count_values(rows, column, sort_by=sort_by, ascending=ascending)
    writer.writeheader()
    for r in results:
        writer.writerow(r)
