import csv
from typing import Iterator


def bin_rows(
    rows: list[dict],
    column: str,
    bins: list[float],
    labels: list[str] | None = None,
    output_column: str = "bin",
) -> list[dict]:
    """Assign each row to a bin based on a numeric column value.

    bins: sorted list of bin edges, e.g. [0, 10, 20, 30]
    creates intervals: <0, 0-10, 10-20, 20-30, >=30
    labels: optional list of len(bins)+1 labels for each interval
    """
    if labels is not None and len(labels) != len(bins) + 1:
        raise ValueError(
            f"Expected {len(bins) + 1} labels for {len(bins)} edges, got {len(labels)}"
        )

    default_labels = (
        [f"<{bins[0]}"]
        + [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins) - 1)]
        + [f">={bins[-1]}"]
    ) if bins else ["all"]

    effective_labels = labels if labels is not None else default_labels

    result = []
    for row in rows:
        raw = row.get(column, "")
        try:
            val = float(raw)
        except (ValueError, TypeError):
            result.append({**row, output_column: ""})
            continue

        if not bins:
            label = effective_labels[0]
        elif val < bins[0]:
            label = effective_labels[0]
        else:
            label = effective_labels[-1]
            for i, edge in enumerate(bins[:-1]):
                if edge <= val < bins[i + 1]:
                    label = effective_labels[i + 1]
                    break

        result.append({**row, output_column: label})
    return result


def bin_file(
    reader: Iterator[dict],
    writer,
    column: str,
    bins: list[float],
    labels: list[str] | None = None,
    output_column: str = "bin",
) -> None:
    rows = list(reader)
    if not rows:
        return
    binned = bin_rows(rows, column, bins, labels, output_column)
    writer.writeheader()
    for row in binned:
        writer.writerow(row)
