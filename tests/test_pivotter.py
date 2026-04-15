"""Tests for csvwrangler.pivotter."""

import pytest

from csvwrangler.pivotter import pivot_rows


SALES = [
    {"region": "North", "product": "A", "revenue": "100"},
    {"region": "North", "product": "B", "revenue": "200"},
    {"region": "South", "product": "A", "revenue": "150"},
    {"region": "South", "product": "B", "revenue": "50"},
    {"region": "North", "product": "A", "revenue": "50"},
]


def _by_index(rows, key, val):
    return next(r for r in rows if r[key] == val)


def test_pivot_sum():
    result = pivot_rows(SALES, index="region", columns="product", values="revenue", aggfunc="sum")
    north = _by_index(result, "region", "North")
    south = _by_index(result, "region", "South")
    assert north["A"] == "150"   # 100 + 50
    assert north["B"] == "200"
    assert south["A"] == "150"
    assert south["B"] == "50"


def test_pivot_count():
    result = pivot_rows(SALES, index="region", columns="product", values="revenue", aggfunc="count")
    north = _by_index(result, "region", "North")
    assert north["A"] == "2"
    assert north["B"] == "1"


def test_pivot_min():
    result = pivot_rows(SALES, index="region", columns="product", values="revenue", aggfunc="min")
    north = _by_index(result, "region", "North")
    assert north["A"] == "50"


def test_pivot_max():
    result = pivot_rows(SALES, index="region", columns="product", values="revenue", aggfunc="max")
    north = _by_index(result, "region", "North")
    assert north["A"] == "100"


def test_pivot_first():
    result = pivot_rows(SALES, index="region", columns="product", values="revenue", aggfunc="first")
    north = _by_index(result, "region", "North")
    assert north["A"] == "100"


def test_pivot_missing_cell_is_empty():
    rows = [
        {"region": "North", "product": "A", "revenue": "10"},
        {"region": "South", "product": "B", "revenue": "20"},
    ]
    result = pivot_rows(rows, index="region", columns="product", values="revenue", aggfunc="sum")
    north = _by_index(result, "region", "North")
    south = _by_index(result, "region", "South")
    assert north["B"] == ""
    assert south["A"] == ""


def test_pivot_invalid_aggfunc():
    with pytest.raises(ValueError, match="Unsupported aggfunc"):
        pivot_rows(SALES, index="region", columns="product", values="revenue", aggfunc="median")


def test_pivot_empty_input():
    result = pivot_rows([], index="region", columns="product", values="revenue")
    assert result == []


def test_pivot_index_column_present_in_output():
    result = pivot_rows(SALES, index="region", columns="product", values="revenue")
    assert all("region" in r for r in result)
