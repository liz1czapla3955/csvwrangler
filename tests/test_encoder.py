"""Tests for csvwrangler.encoder."""
import base64
import urllib.parse
import pytest
from csvwrangler.encoder import encode_rows, _encode_value, _decode_value


ROWS = [
    {"id": "1", "name": "Alice", "note": "hello world"},
    {"id": "2", "name": "Bob",   "note": "foo&bar"},
]


def test_encode_value_base64():
    assert _encode_value("hello", "base64") == base64.b64encode(b"hello").decode()


def test_encode_value_url():
    assert _encode_value("hello world", "url") == "hello%20world"


def test_encode_value_hex():
    assert _encode_value("hi", "hex") == "6869"


def test_decode_value_base64():
    encoded = base64.b64encode(b"hello").decode()
    assert _decode_value(encoded, "base64") == "hello"


def test_decode_value_url():
    assert _decode_value("hello%20world", "url") == "hello world"


def test_decode_value_hex():
    assert _decode_value("6869", "hex") == "hi"


def test_encode_rows_base64():
    result = list(encode_rows(ROWS, ["note"], "base64"))
    assert result[0]["note"] == base64.b64encode(b"hello world").decode()
    assert result[0]["id"] == "1"  # unchanged


def test_encode_rows_url():
    result = list(encode_rows(ROWS, ["note"], "url"))
    assert result[1]["note"] == urllib.parse.quote("foo&bar", safe="")


def test_encode_rows_hex_multiple_columns():
    result = list(encode_rows(ROWS, ["name", "note"], "hex"))
    assert result[0]["name"] == "Alice".encode().hex()
    assert result[0]["note"] == "hello world".encode().hex()


def test_decode_rows_roundtrip():
    encoded = list(encode_rows(ROWS, ["note"], "base64"))
    decoded = list(encode_rows(encoded, ["note"], "base64", decode=True))
    assert decoded[0]["note"] == ROWS[0]["note"]
    assert decoded[1]["note"] == ROWS[1]["note"]


def test_encode_rows_missing_column_raises():
    with pytest.raises(KeyError, match="missing"):
        list(encode_rows(ROWS, ["missing"], "hex"))


def test_encode_rows_unsupported_encoding_raises():
    with pytest.raises(ValueError, match="Unsupported encoding"):
        list(encode_rows(ROWS, ["note"], "rot13"))
