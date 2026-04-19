"""Condense repeated header-value pairs into a single summary column."""

import csv
import io
from typing import Iterable, Iterator


def condense_rows(
    rows: Iterable[dict],
    columns: list[str],
    output_column: str = "summary",
    separator: str = "; ",
    template: str = "{col}={val}",
    skip_empty: bool = True,
) -> Iterator[dict]:
    """Yield rows with selected columns condensed into a single string column.

    Args:
        rows: Iterable of row dicts.
        columns: Column names to condense.
        output_column: Name of the new summary column.
        separator: String used to join pairs.
        template: Format string with {col} and {val} placeholders.
        skip_empty: If True, skip pairs where value is empty.
    """
    for row in rows:
        parts = []
        for col in columns:
            val = row.get(col, "")
            if skip_empty and val == "":
                continue
            parts.append(template.format(col=col, val=val))
        out = dict(row)
        out[output_column] = separator.join(parts)
        yield out


def condense_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    columns: list[str],
    output_column: str = "summary",
    separator: str = "; ",
    template: str = "{col}={val}",
    skip_empty: bool = True,
) -> None:
    """Read from reader, condense columns, write to writer."""
    first = True
    for row in condense_rows(
        reader,
        columns=columns,
        output_column=output_column,
        separator=separator,
        template=template,
        skip_empty=skip_empty,
    ):
        if first:
            writer.fieldnames = list(row.keys())
            writer.writeheader()
            first = False
        writer.writerow(row)
