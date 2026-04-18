import csv
from typing import Iterable, Iterator


def rolling_rows(
    rows: Iterable[dict],
    column: str,
    window: int,
    agg: str = "mean",
    output_column: str | None = None,
) -> Iterator[dict]:
    """Compute a rolling window aggregation over a numeric column."""
    if window < 1:
        raise ValueError("window must be >= 1")
    valid_aggs = {"mean", "sum", "min", "max"}
    if agg not in valid_aggs:
        raise ValueError(f"agg must be one of {sorted(valid_aggs)}")

    out_col = output_column or f"{column}_rolling_{agg}"
    buffer: list[float] = []

    for row in rows:
        raw = row.get(column, "")
        try:
            val = float(raw)
            buffer.append(val)
        except (ValueError, TypeError):
            yield {**row, out_col: ""}
            continue

        if len(buffer) > window:
            buffer.pop(0)

        window_vals = buffer[-window:]
        if agg == "mean":
            result = sum(window_vals) / len(window_vals)
        elif agg == "sum":
            result = sum(window_vals)
        elif agg == "min":
            result = min(window_vals)
        else:
            result = max(window_vals)

        yield {**row, out_col: str(round(result, 10)).rstrip("0").rstrip(".")}


def rolling_file(
    reader: Iterable[dict],
    writer,
    column: str,
    window: int,
    agg: str = "mean",
    output_column: str | None = None,
) -> None:
    rows = list(reader)
    if not rows:
        return
    result = list(rolling_rows(rows, column, window, agg, output_column))
    writer.writeheader()
    for row in result:
        writer.writerow(row)
