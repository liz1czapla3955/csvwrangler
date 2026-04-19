import pytest
from csvwrangler.limiter import limit_rows


def _rows(n=5):
    return [{"id": str(i), "val": str(i * 10)} for i in range(1, n + 1)]


def test_limit_basic():
    result = limit_rows(_rows(), limit=3)
    assert len(result) == 3
    assert result[0]["id"] == "1"
    assert result[2]["id"] == "3"


def test_limit_with_offset():
    result = limit_rows(_rows(), limit=2, offset=2)
    assert len(result) == 2
    assert result[0]["id"] == "3"
    assert result[1]["id"] == "4"


def test_limit_zero_returns_empty():
    result = limit_rows(_rows(), limit=0)
    assert result == []


def test_limit_exceeds_rows():
    result = limit_rows(_rows(3), limit=100)
    assert len(result) == 3


def test_offset_exceeds_rows():
    result = limit_rows(_rows(3), limit=10, offset=10)
    assert result == []


def test_offset_zero_same_as_default():
    a = limit_rows(_rows(), limit=3)
    b = limit_rows(_rows(), limit=3, offset=0)
    assert a == b


def test_negative_limit_raises():
    with pytest.raises(ValueError, match="limit"):
        limit_rows(_rows(), limit=-1)


def test_negative_offset_raises():
    with pytest.raises(ValueError, match="offset"):
        limit_rows(_rows(), limit=2, offset=-1)


def test_empty_input():
    result = limit_rows([], limit=5)
    assert result == []


def test_limit_one():
    result = limit_rows(_rows(), limit=1)
    assert len(result) == 1
    assert result[0]["id"] == "1"
