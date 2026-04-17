import csv
import io
import re
from typing import Iterable, Iterator


def replace_values(
    rows: Iterable[dict],
    column: str,
    pattern: str,
    replacement: str,
    use_regex: bool = False,
    case_sensitive: bool = True,
) -> Iterator[dict]:
    """Replace values in a column by exact match or regex."""
    flags = 0 if case_sensitive else re.IGNORECASE
    for row in rows:
        if column not in row:
            raise KeyError(f"Column '{column}' not found in row")
        new_row = dict(row)
        value = new_row[column]
        if use_regex:
            new_row[column] = re.sub(pattern, replacement, value, flags=flags)
        else:
            if case_sensitive:
                new_row[column] = value.replace(pattern, replacement)
            else:
                compiled = re.compile(re.escape(pattern), flags)
                new_row[column] = compiled.sub(replacement, value)
        yield new_row


def replace_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    pattern: str,
    replacement: str,
    use_regex: bool = False,
    case_sensitive: bool = True,
) -> None:
    writer.writeheader()
    for row in replace_values(
        reader, column, pattern, replacement, use_regex, case_sensitive
    ):
        writer.writerow(row)
