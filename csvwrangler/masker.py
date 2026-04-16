"""Masking/redacting CSV column values."""
import csv
import io
import re
from typing import Iterable, Iterator


MASK_MODES = ("full", "partial", "hash", "redact")


def _mask_value(value: str, mode: str, char: str = "*") -> str:
    if mode == "full":
        return char * len(value)
    elif mode == "partial":
        if len(value) <= 4:
            return char * len(value)
        visible = max(1, len(value) // 4)
        return value[:visible] + char * (len(value) - visible)
    elif mode == "hash":
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    elif mode == "redact":
        return "[REDACTED]"
    else:
        raise ValueError(f"Unknown mask mode: {mode!r}. Choose from {MASK_MODES}.")


def mask_rows(
    rows: Iterable[dict],
    columns: list[str],
    mode: str = "full",
    char: str = "*",
) -> Iterator[dict]:
    if mode not in MASK_MODES:
        raise ValueError(f"Unknown mask mode: {mode!r}. Choose from {MASK_MODES}.")
    for row in rows:
        out = dict(row)
        for col in columns:
            if col in out:
                out[col] = _mask_value(out[col], mode, char)
        yield out


def mask_file(
    input_text: str,
    columns: list[str],
    mode: str = "full",
    char: str = "*",
) -> str:
    reader = csv.DictReader(io.StringIO(input_text))
    if not reader.fieldnames:
        return input_text
    rows = list(mask_rows(reader, columns, mode, char))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()
