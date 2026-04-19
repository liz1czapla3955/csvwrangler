"""Column-level value comparison and flagging."""
from typing import Iterator


def _compare(a: str, b: str, op: str) -> bool:
    """Compare two string values using the given operator.

    Attempts numeric comparison first; falls back to string comparison
    for equality operators. Raises ValueError for unsupported operators.
    """
    try:
        fa, fb = float(a), float(b)
        if op == "eq": return fa == fb
        if op == "ne": return fa != fb
        if op == "lt": return fa < fb
        if op == "le": return fa <= fb
        if op == "gt": return fa > fb
        if op == "ge": return fa >= fb
    except (ValueError, TypeError):
        if op == "eq": return a == b
        if op == "ne": return a != b
        if op in ("lt", "le", "gt", "ge"):
            raise ValueError(
                f"Operator '{op}' requires numeric values, but got: {a!r}, {b!r}"
            )
    raise ValueError(f"Unsupported operator: {op}")


def compare_rows(
    rows: Iterator[dict],
    col_a: str,
    col_b: str,
    op: str,
    output_col: str = "match",
    true_val: str = "true",
    false_val: str = "false",
) -> Iterator[dict]:
    """Yield rows with an added column indicating comparison result."""
    for row in rows:
        a = row.get(col_a, "")
        b = row.get(col_b, "")
        try:
            result = _compare(a, b, op)
        except ValueError:
            result = False
        yield {**row, output_col: true_val if result else false_val}


def compare_file(reader, writer, col_a, col_b, op, output_col="match", true_val="true", false_val="false"):
    rows = list(reader)
    if not rows:
        return
    out = list(compare_rows(iter(rows), col_a, col_b, op, output_col, true_val, false_val))
    writer.writeheader()
    for row in out:
        writer.writerow(row)
