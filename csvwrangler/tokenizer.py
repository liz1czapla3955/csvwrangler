"""Tokenize string columns into delimited multi-value cells or split them into indicator columns."""

import csv
import io
from typing import Iterable, Iterator


def tokenize_rows(
    rows: Iterable[dict],
    column: str,
    sep: str = " ",
    mode: str = "split",
    output_sep: str = "|",
    prefix: str = "",
    lowercase: bool = False,
) -> Iterator[dict]:
    """Tokenize values in *column* by *sep*.

    mode='split'    – replace the column with a pipe-separated (or *output_sep*) token list.
    mode='indicator' – add one boolean column per unique token found across all rows.
    """
    rows = list(rows)
    if not rows:
        return

    if mode == "split":
        for row in rows:
            raw = row.get(column, "")
            tokens = [t.strip() for t in raw.split(sep) if t.strip()]
            if lowercase:
                tokens = [t.lower() for t in tokens]
            out = dict(row)
            out[column] = output_sep.join(tokens)
            yield out

    elif mode == "indicator":
        # First pass: collect all tokens
        all_tokens: list = []
        seen: set = set()
        for row in rows:
            raw = row.get(column, "")
            for t in raw.split(sep):
                t = t.strip()
                if lowercase:
                    t = t.lower()
                if t and t not in seen:
                    seen.add(t)
                    all_tokens.append(t)

        col_names = [f"{prefix}{t}" for t in all_tokens]

        for row in rows:
            raw = row.get(column, "")
            present = {
                (t.lower() if lowercase else t).strip()
                for t in raw.split(sep)
                if t.strip()
            }
            out = dict(row)
            for token, col_name in zip(all_tokens, col_names):
                out[col_name] = "1" if token in present else "0"
            yield out
    else:
        raise ValueError(f"Unknown mode: {mode!r}. Choose 'split' or 'indicator'.")


def tokenize_file(
    reader: csv.DictReader,
    writer: csv.DictWriter,
    column: str,
    sep: str = " ",
    mode: str = "split",
    output_sep: str = "|",
    prefix: str = "",
    lowercase: bool = False,
) -> None:
    rows = list(reader)
    result = list(
        tokenize_rows(rows, column, sep=sep, mode=mode,
                      output_sep=output_sep, prefix=prefix, lowercase=lowercase)
    )
    if result:
        writer.fieldnames = list(result[0].keys())
        writer.writeheader()
        writer.writerows(result)
