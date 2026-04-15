"""Tests for csvwrangler.validator."""

import pytest
from csvwrangler.validator import _check_value, validate_rows


# --- _check_value ---

def test_check_value_integer_valid():
    assert _check_value("42", "integer") is True

def test_check_value_integer_invalid():
    assert _check_value("3.14", "integer") is False

def test_check_value_float_valid():
    assert _check_value("3.14", "float") is True

def test_check_value_float_invalid():
    assert _check_value("abc", "float") is False

def test_check_value_boolean_valid():
    for val in ("true", "false", "yes", "no", "1", "0", "True", "YES"):
        assert _check_value(val, "boolean") is True

def test_check_value_boolean_invalid():
    assert _check_value("maybe", "boolean") is False

def test_check_value_date_valid():
    assert _check_value("2024-01-15", "date") is True

def test_check_value_date_invalid():
    assert _check_value("15/01/2024", "date") is False

def test_check_value_string_always_valid():
    assert _check_value("anything goes", "string") is True

def test_check_value_empty_always_valid():
    for t in ("integer", "float", "boolean", "date", "string"):
        assert _check_value("", t) is True


# --- validate_rows ---

ROWS = [
    {"id": "1", "name": "Alice", "score": "9.5", "active": "true", "dob": "1990-05-20"},
    {"id": "2", "name": "Bob",   "score": "8.0", "active": "false", "dob": "1985-11-03"},
]

def test_validate_rows_no_violations():
    rules = {"id": "integer", "score": "float", "active": "boolean", "dob": "date"}
    assert validate_rows(ROWS, rules) == []

def test_validate_rows_type_violation():
    bad_rows = [{"id": "abc", "name": "X"}]
    violations = validate_rows(bad_rows, {"id": "integer"})
    assert len(violations) == 1
    assert violations[0]["column"] == "id"
    assert violations[0]["row"] == 1

def test_validate_rows_required_violation():
    rows = [{"id": "1", "name": ""}, {"id": "2", "name": "Bob"}]
    violations = validate_rows(rows, {}, required=["name"])
    assert len(violations) == 1
    assert violations[0]["column"] == "name"
    assert violations[0]["row"] == 1
    assert "required" in violations[0]["reason"]

def test_validate_rows_multiple_violations():
    rows = [
        {"id": "bad", "score": "also_bad", "name": ""},
    ]
    violations = validate_rows(rows, {"id": "integer", "score": "float"}, required=["name"])
    assert len(violations) == 3

def test_validate_rows_missing_column_in_row_skipped():
    rows = [{"name": "Alice"}]  # no 'id' key
    violations = validate_rows(rows, {"id": "integer"})
    assert violations == []

def test_validate_rows_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown type"):
        validate_rows(ROWS, {"id": "uuid"})

def test_validate_rows_empty_input():
    assert validate_rows([], {"id": "integer"}, required=["id"]) == []
