"""Encode/decode CSV column values (base64, url, hex)."""
import csv
import io
import base64
import urllib.parse
from typing import Iterable, Iterator

SUPPORTED_ENCODINGS = ("base64", "url", "hex")


def _encode_value(value: str, encoding: str) -> str:
    if encoding == "base64":
        return base64.b64encode(value.encode()).decode()
    if encoding == "url":
        return urllib.parse.quote(value, safe="")
    if encoding == "hex":
        return value.encode().hex()
    raise ValueError(f"Unsupported encoding: {encoding}")


def _decode_value(value: str, encoding: str) -> str:
    if encoding == "base64":
        return base64.b64decode(value.encode()).decode()
    if encoding == "url":
        return urllib.parse.unquote(value)
    if encoding == "hex":
        return bytes.fromhex(value).decode()
    raise ValueError(f"Unsupported encoding: {encoding}")


def encode_rows(
    rows: Iterable[dict],
    columns: list[str],
    encoding: str,
    decode: bool = False,
) -> Iterator[dict]:
    """Encode or decode specified columns in each row."""
    if encoding not in SUPPORTED_ENCODINGS:
        raise ValueError(f"Unsupported encoding '{encoding}'. Choose from {SUPPORTED_ENCODINGS}.")
    fn = _decode_value if decode else _encode_value
    for row in rows:
        new_row = dict(row)
        for col in columns:
            if col not in new_row:
                raise KeyError(f"Column '{col}' not found in row.")
            new_row[col] = fn(new_row[col], encoding)
        yield new_row


def encode_file(
    input_path: str,
    output_path: str,
    columns: list[str],
    encoding: str,
    decode: bool = False,
) -> None:
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(encode_rows(reader, columns, encoding, decode=decode))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
