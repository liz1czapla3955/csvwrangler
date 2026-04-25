"""Extract rows matching a regex pattern from one or more columns."""
import re
from typing import Iterator


def extract_rows(
    rows: Iterator[dict],
    columns: list[str],
    pattern: str,
    invert: bool = False,
    output_column: str | None = None,
) -> Iterator[dict]:
    """Yield rows where any of the given columns match *pattern*.

    Parameters
    ----------
    rows:          Input row dicts.
    columns:       Column names to search.
    pattern:       Regular-expression pattern string.
    invert:        When True, yield rows that do NOT match.
    output_column: If given, add a column with the first capturing group
                   (or the full match when no groups are defined).
    """
    compiled = re.compile(pattern)

    for row in rows:
        match_obj = None
        for col in columns:
            value = row.get(col, "")
            m = compiled.search(str(value))
            if m:
                match_obj = m
                break

        matched = match_obj is not None
        if invert:
            matched = not matched

        if matched:
            out = dict(row)
            if output_column is not None:
                if match_obj is not None:
                    groups = match_obj.groups()
                    out[output_column] = groups[0] if groups else match_obj.group(0)
                else:
                    out[output_column] = ""
            yield out


def extract_file(
    reader,
    writer,
    columns: list[str],
    pattern: str,
    invert: bool = False,
    output_column: str | None = None,
) -> None:
    """Stream-extract rows from *reader* and write results to *writer*."""
    rows = iter(reader)
    results = extract_rows(rows, columns, pattern, invert=invert, output_column=output_column)
    first = next(results, None)
    if first is None:
        return
    fieldnames = list(first.keys())
    writer.writeheader() if hasattr(writer, "fieldnames") else None
    writer.writerow(first)
    for row in results:
        writer.writerow(row)
