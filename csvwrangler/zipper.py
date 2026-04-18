"""Zip (interleave) two CSV row sequences by position or merge by a key column."""
from __future__ import annotations

import csv
import io
from typing import Iterator


def zip_rows(
    rows_a: list[dict],
    rows_b: list[dict],
    how: str = "position",
    key: str | None = None,
) -> list[dict]:
    """Merge two lists of rows.

    how='position' – pair rows by index (shorter list truncates).
    how='left'     – keep all rows from rows_a, fill missing b-cols with ''.
    how='key'      – join on *key* column (inner join by key).
    """
    if how == "position":
        result = []
        for a, b in zip(rows_a, rows_b):
            merged = dict(a)
            for k, v in b.items():
                if k in merged and k != key:
                    merged[f"{k}_b"] = v
                else:
                    merged[k] = v
            result.append(merged)
        return result

    if how == "left":
        index_b: dict[str, dict] = {}
        if key is None:
            raise ValueError("'key' column required for how='left'")
        for row in rows_b:
            index_b[row[key]] = row
        result = []
        all_b_keys = list(rows_b[0].keys()) if rows_b else []
        for row in rows_a:
            k_val = row.get(key, "")
            b_row = index_b.get(k_val, {bk: "" for bk in all_b_keys})
            merged = dict(row)
            for bk, bv in b_row.items():
                if bk == key:
                    continue
                if bk in merged:
                    merged[f"{bk}_b"] = bv
                else:
                    merged[bk] = bv
            result.append(merged)
        return result

    if how == "key":
        if key is None:
            raise ValueError("'key' column required for how='key'")
        index_b = {row[key]: row for row in rows_b}
        result = []
        for row in rows_a:
            k_val = row.get(key, "")
            if k_val not in index_b:
                continue
            b_row = index_b[k_val]
            merged = dict(row)
            for bk, bv in b_row.items():
                if bk == key:
                    continue
                if bk in merged:
                    merged[f"{bk}_b"] = bv
                else:
                    merged[bk] = bv
            result.append(merged)
        return result

    raise ValueError(f"Unknown how='{how}'. Choose position, left, or key.")


def zip_files(
    reader_a: csv.DictReader,
    reader_b: csv.DictReader,
    writer: csv.DictWriter | None,
    how: str = "position",
    key: str | None = None,
) -> list[dict]:
    rows_a = list(reader_a)
    rows_b = list(reader_b)
    merged = zip_rows(rows_a, rows_b, how=how, key=key)
    if merged and writer is not None:
        writer.writeheader()
        for row in merged:
            writer.writerow(row)
    return merged
