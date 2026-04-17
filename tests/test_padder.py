import pytest
from csvwrangler.padder import pad_rows


def _rows(*dicts):
    return list(dicts)


def test_pad_right_default():
    rows = _rows({"id": "7", "name": "Alice"})
    result = list(pad_rows(rows, columns=["id"], width=4))
    assert result[0]["id"] == "0007"


def test_pad_left():
    rows = _rows({"code": "AB", "val": "x"})
    result = list(pad_rows(rows, columns=["code"], width=5, fill_char="-", align="left"))
    assert result[0]["code"] == "AB---"


def test_pad_no_truncation():
    rows = _rows({"id": "12345"})
    result = list(pad_rows(rows, columns=["id"], width=3))
    assert result[0]["id"] == "12345"


def test_pad_exact_width():
    rows = _rows({"id": "999"})
    result = list(pad_rows(rows, columns=["id"], width=3))
    assert result[0]["id"] == "999"


def test_pad_multiple_columns():
    rows = _rows({"a": "1", "b": "2", "c": "skip"})
    result = list(pad_rows(rows, columns=["a", "b"], width=3, fill_char="0"))
    assert result[0]["a"] == "001"
    assert result[0]["b"] == "002"
    assert result[0]["c"] == "skip"


def test_pad_missing_column_ignored():
    rows = _rows({"a": "1"})
    result = list(pad_rows(rows, columns=["a", "z"], width=3))
    assert result[0]["a"] == "001"
    assert "z" not in result[0]


def test_pad_invalid_align():
    with pytest.raises(ValueError, match="align"):
        list(pad_rows([{"a": "1"}], columns=["a"], width=3, align="center"))


def test_pad_invalid_fill_char():
    with pytest.raises(ValueError, match="fill_char"):
        list(pad_rows([{"a": "1"}], columns=["a"], width=3, fill_char="xx"))


def test_pad_invalid_width():
    with pytest.raises(ValueError, match="width"):
        list(pad_rows([{"a": "1"}], columns=["a"], width=0))


def test_pad_empty_input():
    result = list(pad_rows([], columns=["a"], width=5))
    assert result == []


def test_pad_preserves_other_fields():
    rows = _rows({"id": "3", "name": "Bob", "score": "99"})
    result = list(pad_rows(rows, columns=["id"], width=4))
    assert result[0]["name"] == "Bob"
    assert result[0]["score"] == "99"
