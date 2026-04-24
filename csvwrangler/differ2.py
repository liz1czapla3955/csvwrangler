"""Row-level frequency analysis: count how often each unique value appears per column."""
import csv
import io
from collections import Counter
from typing import Iterable, Iterator


def frequency_rows(
    rows: Iterable[dict],
    column: str,
    output_column: str = "frequency",
    sort_by: str = "count",
    ascending: bool = False,
) -> list[dict]:
    """Return frequency table rows for *column*.

    Each output row has two fields: the original column value and *output_column*
    (the count).  *sort_by* is either ``'value'`` or ``'count'``.
    """
    counts: Counter = Counter()
    for row in rows:
        if column not in row:
            raise KeyError(f"Column '{column}' not found in row: {list(row.keys())}")
        counts[row[column]] += 1

    result = [{column: val, output_column: str(cnt)} for val, cnt in counts.items()]

    if sort_by == "count":
        result.sort(key=lambda r: int(r[output_column]), reverse=not ascending)
    elif sort_by == "value":
        result.sort(key=lambda r: r[column], reverse=not ascending)
    else:
        raise ValueError(f"sort_by must be 'count' or 'value', got '{sort_by}'")

    return result


def frequency_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    output_column: str = "frequency",
    sort_by: str = "count",
    ascending: bool = False,
) -> None:
    """Read *reader*, compute frequency for *column*, write results to *writer*."""
    rows = frequency_rows(
        reader,
        column=column,
        output_column=output_column,
        sort_by=sort_by,
        ascending=ascending,
    )
    if rows:
        writer.fieldnames = list(rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
