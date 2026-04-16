"""Tests for csvwrangler.masker."""
import pytest
from csvwrangler.masker import _mask_value, mask_rows, mask_file


def test_mask_value_full():
    assert _mask_value("hello", "full") == "*****"


def test_mask_value_full_custom_char():
    assert _mask_value("abc", "full", char="#") == "###"


def test_mask_value_partial_long():
    result = _mask_value("abcdefgh", "partial")
    assert result[0] == "a" or result[0] == "ab"
    assert "*" in result
    assert len(result) == 8


def test_mask_value_partial_short():
    assert _mask_value("ab", "partial") == "**"


def test_mask_value_hash():
    result = _mask_value("secret", "hash")
    assert len(result) == 16
    assert result == _mask_value("secret", "hash")  # deterministic


def test_mask_value_redact():
    assert _mask_value("anything", "redact") == "[REDACTED]"


def test_mask_value_invalid_mode():
    with pytest.raises(ValueError, match="Unknown mask mode"):
        _mask_value("x", "unknown")


def test_mask_rows_single_column():
    rows = [{"name": "Alice", "email": "alice@example.com"}]
    result = list(mask_rows(rows, columns=["email"], mode="redact"))
    assert result[0]["email"] == "[REDACTED]"
    assert result[0]["name"] == "Alice"


def test_mask_rows_multiple_columns():
    rows = [{"a": "foo", "b": "bar", "c": "baz"}]
    result = list(mask_rows(rows, columns=["a", "b"], mode="full"))
    assert result[0]["a"] == "***"
    assert result[0]["b"] == "***"
    assert result[0]["c"] == "baz"


def test_mask_rows_missing_column_ignored():
    rows = [{"x": "hello"}]
    result = list(mask_rows(rows, columns=["y"], mode="full"))
    assert result[0] == {"x": "hello"}


def test_mask_rows_invalid_mode_raises():
    with pytest.raises(ValueError):
        list(mask_rows([{"a": "1"}], columns=["a"], mode="bad"))


def test_mask_file_full():
    csv_text = "name,phone\nAlice,555-1234\nBob,555-5678\n"
    result = mask_file(csv_text, columns=["phone"], mode="full")
    assert "555-1234" not in result
    assert "name,phone" in result


def test_mask_file_empty():
    result = mask_file("", columns=["a"])
    assert result == ""


def test_mask_file_hash_deterministic():
    csv_text = "id,secret\n1,mysecret\n"
    r1 = mask_file(csv_text, columns=["secret"], mode="hash")
    r2 = mask_file(csv_text, columns=["secret"], mode="hash")
    assert r1 == r2
