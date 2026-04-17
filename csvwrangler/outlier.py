import csv
import io
import math
from typing import Iterable, Iterator


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _stddev(values: list[float], mean: float) -> float:
    if len(values) < 2:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def detect_outliers(
    rows: Iterable[dict],
    column: str,
    threshold: float = 3.0,
    mark: bool = False,
    mark_column: str = "is_outlier",
) -> Iterator[dict]:
    """Detect outliers in a numeric column using z-score method."""
    all_rows = list(rows)
    values: list[float] = []
    for row in all_rows:
        try:
            values.append(float(row[column]))
        except (ValueError, KeyError):
            pass

    if not values:
        yield from all_rows
        return

    mean = _mean(values)
    std = _stddev(values, mean)

    for row in all_rows:
        try:
            z = abs((float(row[column]) - mean) / std) if std else 0.0
            is_outlier = z > threshold
        except (ValueError, KeyError):
            is_outlier = False

        if mark:
            yield {**row, mark_column: "1" if is_outlier else "0"}
        elif is_outlier:
            yield row
        else:
            if not mark:
                yield row


def outlier_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    threshold: float = 3.0,
    mark: bool = False,
    mark_column: str = "is_outlier",
) -> None:
    rows = list(reader)
    result = list(detect_outliers(rows, column, threshold, mark, mark_column))
    if result:
        fieldnames = list(result[0].keys())
        writer.fieldnames = fieldnames
        writer.writeheader()
        writer.writerows(result)
