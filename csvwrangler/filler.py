"""Fill missing values in CSV columns with a constant, mean, or forward-fill."""
import csv
import io
from typing import Iterable, Iterator


def _mean(values: list[str]) -> str:
    nums = []
    for v in values:
        try:
            nums.append(float(v))
        except (ValueError, TypeError):
            pass
    if not nums:
        return ""
    avg = sum(nums) / len(nums)
    return str(int(avg) if avg == int(avg) else avg)


def fill_rows(
    rows: Iterable[dict],
    columns: list[str],
    method: str = "value",
    fill_value: str = "",
) -> Iterator[dict]:
    """Yield rows with missing values filled.

    method: 'value' (constant), 'mean', 'ffill'
    """
    rows = list(rows)
    if not rows:
        return

    fieldnames = list(rows[0].keys())
    target_cols = columns if columns else fieldnames

    if method == "mean":
        means = {col: _mean([r.get(col, "") for r in rows]) for col in target_cols}

    last_seen: dict[str, str] = {col: "" for col in target_cols}

    for row in rows:
        new_row = dict(row)
        for col in target_cols:
            if col not in new_row:
                continue
            val = new_row[col]
            if val == "" or val is None:
                if method == "value":
                    new_row[col] = fill_value
                elif method == "mean":
                    new_row[col] = means[col]
                elif method == "ffill":
                    new_row[col] = last_seen[col]
            else:
                last_seen[col] = val
        yield new_row


def fill_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    method: str = "value",
    fill_value: str = "",
) -> None:
    writer.writeheader()
    for row in fill_rows(reader, columns, method=method, fill_value=fill_value):
        writer.writerow(row)
