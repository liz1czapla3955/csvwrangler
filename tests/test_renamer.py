"""Tests for csvwrangler.renamer."""

from __future__ import annotations

import pytest

from csvwrangler.renamer import normalize_headers, normalize_values, normalize_file


# ---------------------------------------------------------------------------
# normalize_headers
# ---------------------------------------------------------------------------

def test_normalize_headers_strip():
    rows = [{" Name ": "Alice", " Age ": "30"}]
    result = normalize_headers(rows, strip=True)
    assert list(result[0].keys()) == ["Name", "Age"]


def test_normalize_headers_lower():
    rows = [{"First Name": "Alice", "Last Name": "Smith"}]
    result = normalize_headers(rows, case="lower")
    assert list(result[0].keys()) == ["first name", "last name"]


def test_normalize_headers_upper():
    rows = [{"city": "London"}]
    result = normalize_headers(rows, case="upper")
    assert list(result[0].keys()) == ["CITY"]


def test_normalize_headers_title():
    rows = [{"full name": "Bob"}]
    result = normalize_headers(rows, case="title")
    assert list(result[0].keys()) == ["Full Name"]


def test_normalize_headers_replace():
    rows = [{"first name": "Alice", "last name": "Smith"}]
    result = normalize_headers(rows, replace={" ": "_"})
    assert list(result[0].keys()) == ["first_name", "last_name"]


def test_normalize_headers_empty():
    assert normalize_headers([]) == []


def test_normalize_headers_values_preserved():
    rows = [{"Name": "Alice"}, {"Name": "Bob"}]
    result = normalize_headers(rows, case="lower")
    assert [r["name"] for r in result] == ["Alice", "Bob"]


# ---------------------------------------------------------------------------
# normalize_values
# ---------------------------------------------------------------------------

def test_normalize_values_strip():
    rows = [{"name": "  Alice  ", "city": " London "}]
    result = normalize_values(rows, strip=True)
    assert result[0] == {"name": "Alice", "city": "London"}


def test_normalize_values_lower():
    rows = [{"name": "Alice", "city": "London"}]
    result = normalize_values(rows, case="lower")
    assert result[0] == {"name": "alice", "city": "london"}


def test_normalize_values_upper():
    rows = [{"status": "active"}]
    result = normalize_values(rows, case="upper")
    assert result[0]["status"] == "ACTIVE"


def test_normalize_values_specific_columns():
    rows = [{"name": "alice", "city": "london"}]
    result = normalize_values(rows, columns=["name"], case="title")
    assert result[0]["name"] == "Alice"
    assert result[0]["city"] == "london"  # untouched


def test_normalize_values_empty():
    assert normalize_values([]) == []


# ---------------------------------------------------------------------------
# normalize_file
# ---------------------------------------------------------------------------

def test_normalize_file_roundtrip():
    csv_text = " Name , Age \n Alice , 30 \n Bob , 25 \n"
    result = normalize_file(csv_text, header_case="lower", value_case=None, strip=True)
    assert "name" in result
    assert "age" in result
    assert "Alice" in result


def test_normalize_file_empty():
    assert normalize_file("") == ""


def test_normalize_file_replace_space_in_headers():
    csv_text = "first name,last name\nAlice,Smith\n"
    result = normalize_file(csv_text, replace={" ": "_"})
    assert "first_name" in result
    assert "last_name" in result
