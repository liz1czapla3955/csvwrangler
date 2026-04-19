import csv
import io
from collections import defaultdict


def profile_rows(rows):
    """Compute basic profile stats for each column in rows."""
    rows = list(rows)
    if not rows:
        return []

    fieldnames = list(rows[0].keys())
    stats = {f: {"count": 0, "empty": 0, "unique": set(), "min_len": None, "max_len": 0} for f in fieldnames}

    for row in rows:
        for f in fieldnames:
            val = row.get(f, "")
            s = stats[f]
            s["count"] += 1
            if val == "" or val is None:
                s["empty"] += 1
            else:
                s["unique"].add(val)
                l = len(str(val))
                s["max_len"] = max(s["max_len"], l)
                s["min_len"] = l if s["min_len"] is None else min(s["min_len"], l)

    result = []
    for f in fieldnames:
        s = stats[f]
        filled = s["count"] - s["empty"]
        result.append({
            "column": f,
            "count": s["count"],
            "empty": s["empty"],
            "filled": filled,
            "unique": len(s["unique"]),
            "fill_rate": f"{filled / s['count']:.2%}" if s["count"] else "0.00%",
            "min_len": s["min_len"] if s["min_len"] is not None else 0,
            "max_len": s["max_len"],
        })
    return result


def profile_file(reader, writer):
    rows = list(reader)
    profile = profile_rows(rows)
    if not profile:
        return
    writer.writeheader()
    for row in profile:
        writer.writerow(row)
