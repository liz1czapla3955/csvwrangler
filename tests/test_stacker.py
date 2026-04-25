"""Unit tests for csvwrangler.stacker."""
import pytest
from csvwrangler.stacker import stack_rows


def _rows(*dicts):
    return list(dicts)


def test_stack_basic_same_columns():
    a = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
    b = [{"name": "Carol", "age": "40"}]
    result = stack_rows([a, b])
    assert len(result) == 3
    assert result[0] == {"name": "Alice", "age": "30"}
    assert result[2] == {"name": "Carol", "age": "40"}


def test_stack_empty_sources():
    assert stack_rows([]) == []


def test_stack_single_source():
    a = [{"x": "1"}, {"x": "2"}]
    assert stack_rows([a]) == a


def test_stack_missing_column_fill_default():
    a = [{"name": "Alice", "age": "30"}]
    b = [{"name": "Bob", "city": "NYC"}]
    result = stack_rows([a, b])
    assert result[0] == {"name": "Alice", "age": "30", "city": ""}
    assert result[1] == {"name": "Bob", "age": "", "city": "NYC"}


def test_stack_missing_column_fill_custom():
    a = [{"x": "1"}]
    b = [{"y": "2"}]
    result = stack_rows([a, b], fill_value="N/A")
    assert result[0]["y"] == "N/A"
    assert result[1]["x"] == "N/A"


def test_stack_column_order_first_source_first():
    a = [{"b": "1", "a": "2"}]
    b = [{"c": "3", "a": "4"}]
    result = stack_rows([a, b])
    keys = list(result[0].keys())
    assert keys[0] == "b"
    assert "a" in keys
    assert "c" in keys


def test_stack_strict_raises_on_mismatch():
    a = [{"name": "Alice", "age": "30"}]
    b = [{"name": "Bob", "city": "NYC"}]
    with pytest.raises(ValueError, match="Column mismatch"):
        stack_rows([a, b], strict=True)


def test_stack_strict_passes_same_columns():
    a = [{"name": "Alice", "age": "30"}]
    b = [{"name": "Bob", "age": "25"}]
    result = stack_rows([a, b], strict=True)
    assert len(result) == 2


def test_stack_three_sources():
    a = [{"v": "1"}]
    b = [{"v": "2"}]
    c = [{"v": "3"}]
    result = stack_rows([a, b, c])
    assert [r["v"] for r in result] == ["1", "2", "3"]


def test_stack_empty_source_in_list():
    a = [{"x": "1"}]
    b = []
    c = [{"x": "3"}]
    result = stack_rows([a, b, c])
    assert len(result) == 2
    assert result[1]["x"] == "3"
