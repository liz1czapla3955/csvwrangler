"""Format CSV column values: date reformatting, number formatting, zero-padding."""
import csv
import io
from typing import Iterable, Iterator
from datetime import datetime


def _format_value(value: str, fmt_type: str, fmt_arg: str) -> str:
    if fmt_type == "date":
        # fmt_arg: "input_fmt->output_fmt"
        parts = fmt_arg.split("->")
        if len(parts) != 2:
            return value
        in_fmt, out_fmt = parts
        try:
            return datetime.strptime(value.strip(), in_fmt).strftime(out_fmt)
        except ValueError:
            return value
    elif fmt_type == "number":
        # fmt_arg: python format spec e.g. ".2f"
        try:
            return format(float(value), fmt_arg)
        except ValueError:
            return value
    elif fmt_type == "zeropad":
        # fmt_arg: width as string
        try:
            width = int(fmt_arg)
            return value.zfill(width)
        except ValueError:
            return value
    elif fmt_type == "upper":
        return value.upper()
    elif fmt_type == "lower":
        return value.lower()
    elif fmt_type == "title":
        return value.title()
    return value


def format_rows(
    rows: Iterable[dict],
    column: str,
    fmt_type: str,
    fmt_arg: str = "",
) -> Iterator[dict]:
    for row in rows:
        out = dict(row)
        if column in out:
            out[column] = _format_value(out[column], fmt_type, fmt_arg)
        yield out


def format_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    fmt_type: str,
    fmt_arg: str = "",
) -> None:
    writer.writeheader()
    for row in format_rows(reader, column, fmt_type, fmt_arg):
        writer.writerow(row)
