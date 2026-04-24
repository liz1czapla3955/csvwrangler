"""Strip leading/trailing rows from a CSV (blank rows, comment rows, or by count)."""

import csv
import io
from typing import Iterator, List, Optional


def strip_rows(
    rows: List[dict],
    strip_blank: bool = True,
    comment_prefix: Optional[str] = None,
    head: int = 0,
    tail: int = 0,
) -> List[dict]:
    """Return rows with leading/trailing blank or comment rows removed.

    Args:
        rows: Input list of row dicts.
        strip_blank: If True, remove rows where all values are empty strings.
        comment_prefix: If set, remove rows whose first column value starts with this prefix.
        head: Number of rows to strip from the start (applied after other filters).
        tail: Number of rows to strip from the end (applied after other filters).

    Returns:
        Filtered list of row dicts.
    """
    result = list(rows)

    if strip_blank:
        result = [r for r in result if any(v.strip() for v in r.values())]

    if comment_prefix:
        def _is_comment(row: dict) -> bool:
            if not row:
                return False
            first_val = next(iter(row.values()), "")
            return first_val.startswith(comment_prefix)

        result = [r for r in result if not _is_comment(r)]

    if head > 0:
        result = result[head:]

    if tail > 0:
        result = result[:-tail] if tail < len(result) else []

    return result


def strip_file(
    reader: Iterator[dict],
    writer,
    strip_blank: bool = True,
    comment_prefix: Optional[str] = None,
    head: int = 0,
    tail: int = 0,
) -> None:
    """Read rows from reader, strip as configured, write to writer."""
    rows = list(reader)
    if not rows:
        return

    writer.writeheader()
    for row in strip_rows(
        rows,
        strip_blank=strip_blank,
        comment_prefix=comment_prefix,
        head=head,
        tail=tail,
    ):
        writer.writerow(row)
