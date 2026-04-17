import pytest
from csvwrangler.replacer import replace_values


ROWS = [
    {"id": "1", "name": "Alice Smith", "city": "New York"},
    {"id": "2", "name": "Bob Smith", "city": "new york"},
    {"id": "3", "name": "Charlie Brown", "city": "Boston"},
]


def _run(rows, **kwargs):
    return list(replace_values(rows, **kwargs))


def test_replace_exact_match():
    result = _run(ROWS, column="name", pattern="Smith", replacement="Jones")
    assert result[0]["name"] == "Alice Jones"
    assert result[1]["name"] == "Bob Jones"
    assert result[2]["name"] == "Charlie Brown"


def test_replace_no_match():
    result = _run(ROWS, column="city", pattern="London", replacement="Paris")
    assert [r["city"] for r in result] == ["New York", "new york", "Boston"]


def test_replace_case_sensitive_default():
    result = _run(ROWS, column="city", pattern="new york", replacement="LA")
    assert result[0]["city"] == "New York"
    assert result[1]["city"] == "LA"


def test_replace_case_insensitive():
    result = _run(
        ROWS, column="city", pattern="new york", replacement="LA", case_sensitive=False
    )
    assert result[0]["city"] == "LA"
    assert result[1]["city"] == "LA"
    assert result[2]["city"] == "Boston"


def test_replace_regex():
    result = _run(
        ROWS, column="name", pattern=r"\bSmith\b", replacement="Doe", use_regex=True
    )
    assert result[0]["name"] == "Alice Doe"
    assert result[1]["name"] == "Bob Doe"


def test_replace_regex_case_insensitive():
    result = _run(
        ROWS,
        column="city",
        pattern=r"new york",
        replacement="Chicago",
        use_regex=True,
        case_sensitive=False,
    )
    assert result[0]["city"] == "Chicago"
    assert result[1]["city"] == "Chicago"


def test_replace_missing_column_raises():
    with pytest.raises(KeyError):
        _run(ROWS, column="missing", pattern="x", replacement="y")


def test_replace_preserves_other_columns():
    result = _run(ROWS, column="name", pattern="Alice", replacement="Alicia")
    assert result[0]["id"] == "1"
    assert result[0]["city"] == "New York"


def test_replace_empty_input():
    result = _run([], column="name", pattern="x", replacement="y")
    assert result == []
