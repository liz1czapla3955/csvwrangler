import csv
from typing import Iterator


def rank_rows(
    rows: list[dict],
    column: str,
    rank_column: str = "rank",
    method: str = "dense",
    ascending: bool = True,
) -> list[dict]:
    """Add a rank column based on values in the given column.

    method:
      - 'dense'  : no gaps in ranking (1,2,2,3)
      - 'standard': gaps after ties (1,2,2,4)
      - 'row'   : each row gets a unique rank by order of appearance
    """
    if not rows:
        return []

    if column not in rows[0]:
        raise ValueError(f"Column '{column}' not found in data.")

    def sort_key(r):
        v = r[column]
        try:
            return float(v)
        except (ValueError, TypeError):
            return v

    indexed = list(enumerate(rows))
    indexed.sort(key=lambda t: sort_key(t[1]), reverse=not ascending)

    rank_map = {}
    if method == "row":
        for rank, (orig_idx, _) in enumerate(indexed, start=1):
            rank_map[orig_idx] = rank
    elif method == "dense":
        current_rank = 1
        prev_val = object()
        for rank, (orig_idx, row) in enumerate(indexed, start=1):
            val = sort_key(row)
            if val != prev_val:
                current_rank = rank
                prev_val = val
            rank_map[orig_idx] = current_rank
    elif method == "standard":
        prev_val = object()
        prev_rank = 0
        count = 0
        for rank, (orig_idx, row) in enumerate(indexed, start=1):
            val = sort_key(row)
            if val != prev_val:
                prev_rank = rank
                prev_val = val
            rank_map[orig_idx] = prev_rank
    else:
        raise ValueError(f"Unknown rank method '{method}'. Use 'dense', 'standard', or 'row'.")

    result = []
    for orig_idx, row in enumerate(rows):
        new_row = dict(row)
        new_row[rank_column] = str(rank_map[orig_idx])
        result.append(new_row)
    return result


def rank_file(
    reader,
    writer,
    column: str,
    rank_column: str = "rank",
    method: str = "dense",
    ascending: bool = True,
) -> None:
    rows = list(reader)
    if not rows:
        return
    ranked = rank_rows(rows, column, rank_column, method, ascending)
    writer.writeheader()
    for row in ranked:
        writer.writerow(row)
