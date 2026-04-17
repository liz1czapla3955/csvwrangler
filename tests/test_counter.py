import pytest
from csvwrangler.counter import count_values


ROWS = [
    {"name": "Alice", "dept": "Eng"},
    {"name": "Bob",   "dept": "HR"},
    {"name": "Carol", "dept": "Eng"},
    {"name": "Dave",  "dept": "Eng"},
    {"name": "Eve",   "dept": "HR"},
]


def test_count_values_basic():
    result = count_values(ROWS, "dept")
    counts = {r["value"]: r["count"] for r in result}
    assert counts["Eng"] == 3
    assert counts["HR"] == 2


def test_count_values_sort_by_count_descending():
    result = count_values(ROWS, "dept", sort_by="count", ascending=False)
    assert result[0]["value"] == "Eng"
    assert result[0]["count"] == 3


def test_count_values_sort_by_count_ascending():
    result = count_values(ROWS, "dept", sort_by="count", ascending=True)
    assert result[0]["count"] == 2


def test_count_values_sort_by_value():
    result = count_values(ROWS, "dept", sort_by="value", ascending=True)
    assert result[0]["value"] == "Eng"
    assert result[1]["value"] == "HR"


def test_count_values_sort_by_value_descending():
    result = count_values(ROWS, "dept", sort_by="value", ascending=False)
    assert result[0]["value"] == "HR"


def test_count_values_missing_column():
    with pytest.raises(KeyError, match="missing"):
        count_values(ROWS, "missing")


def test_count_values_invalid_sort_by():
    with pytest.raises(ValueError, match="sort_by"):
        count_values(ROWS, "dept", sort_by="bogus")


def test_count_values_empty_rows():
    result = count_values([], "dept")
    assert result == []


def test_count_values_single_unique():
    rows = [{"x": "a"}, {"x": "a"}, {"x": "a"}]
    result = count_values(rows, "x")
    assert len(result) == 1
    assert result[0]["count"] == 3


def test_count_values_all_unique():
    rows = [{"x": str(i)} for i in range(5)]
    result = count_values(rows, "x")
    assert len(result) == 5
    assert all(r["count"] == 1 for r in result)
