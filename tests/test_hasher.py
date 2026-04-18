import hashlib
import pytest
from csvwrangler.hasher import _hash_value, hash_rows


def _sha256(v):
    return hashlib.sha256(v.encode()).hexdigest()


def _md5(v):
    return hashlib.md5(v.encode()).hexdigest()


ROWS = [
    {"id": "1", "email": "alice@example.com", "name": "Alice"},
    {"id": "2", "email": "bob@example.com", "name": "Bob"},
]


def test_hash_value_sha256():
    assert _hash_value("hello", "sha256") == _sha256("hello")


def test_hash_value_md5():
    assert _hash_value("hello", "md5") == _md5("hello")


def test_hash_rows_adds_suffix_column():
    result = list(hash_rows(ROWS, ["email"]))
    assert "email_hash" in result[0]
    assert "email" in result[0]


def test_hash_rows_correct_value():
    result = list(hash_rows(ROWS, ["email"]))
    assert result[0]["email_hash"] == _sha256("alice@example.com")


def test_hash_rows_multiple_columns():
    result = list(hash_rows(ROWS, ["email", "name"]))
    assert "email_hash" in result[0]
    assert "name_hash" in result[0]


def test_hash_rows_custom_suffix():
    result = list(hash_rows(ROWS, ["email"], suffix="_hashed"))
    assert "email_hashed" in result[0]
    assert "email_hash" not in result[0]


def test_hash_rows_md5_algorithm():
    result = list(hash_rows(ROWS, ["email"], algorithm="md5"))
    assert result[0]["email_hash"] == _md5("alice@example.com")


def test_hash_rows_missing_column_skipped():
    result = list(hash_rows(ROWS, ["nonexistent"]))
    assert "nonexistent_hash" not in result[0]


def test_hash_rows_preserves_other_fields():
    result = list(hash_rows(ROWS, ["email"]))
    assert result[0]["id"] == "1"
    assert result[0]["name"] == "Alice"


def test_hash_rows_empty_input():
    result = list(hash_rows([], ["email"]))
    assert result == []
