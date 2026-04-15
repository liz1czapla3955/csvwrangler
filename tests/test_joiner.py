"""Tests for csvwrangler.joiner."""

import io
import pytest

from csvwrangler.joiner import join_rows, join_files


LEFT = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
]

RIGHT = [
    {"id": "1", "dept": "Engineering"},
    {"id": "2", "dept": "Marketing"},
    {"id": "4", "dept": "Finance"},
]


def test_join_rows_inner():
    result = join_rows(LEFT, RIGHT, key="id", how="inner")
    assert len(result) == 2
    assert result[0] == {"id": "1", "name": "Alice", "dept": "Engineering"}
    assert result[1] == {"id": "2", "name": "Bob", "dept": "Marketing"}


def test_join_rows_left():
    result = join_rows(LEFT, RIGHT, key="id", how="left")
    assert len(result) == 3
    ids = [r["id"] for r in result]
    assert "3" in ids
    carol = next(r for r in result if r["id"] == "3")
    assert "dept" not in carol


def test_join_rows_right():
    result = join_rows(LEFT, RIGHT, key="id", how="right")
    ids = [r["id"] for r in result]
    assert "4" in ids
    finance = next(r for r in result if r["id"] == "4")
    assert finance["dept"] == "Finance"


def test_join_rows_column_conflict():
    left = [{"id": "1", "dept": "Left"}]
    right = [{"id": "1", "dept": "Right"}]
    result = join_rows(left, right, key="id", how="inner")
    assert result[0]["dept"] == "Left"
    assert result[0]["dept_right"] == "Right"


def test_join_rows_invalid_how():
    with pytest.raises(ValueError, match="Unsupported join type"):
        join_rows(LEFT, RIGHT, key="id", how="outer")


def test_join_rows_no_matches_inner():
    right_no_match = [{"id": "99", "dept": "X"}]
    result = join_rows(LEFT, right_no_match, key="id", how="inner")
    assert result == []


def test_join_files_inner():
    left_csv = "id,name\n1,Alice\n2,Bob\n"
    right_csv = "id,dept\n1,Engineering\n2,Marketing\n"
    output = io.StringIO()
    count = join_files(
        io.StringIO(left_csv),
        io.StringIO(right_csv),
        output,
        key="id",
        how="inner",
    )
    assert count == 2
    result = output.getvalue()
    assert "Alice" in result
    assert "Engineering" in result


def test_join_files_empty_result():
    left_csv = "id,name\n1,Alice\n"
    right_csv = "id,dept\n9,Finance\n"
    output = io.StringIO()
    count = join_files(
        io.StringIO(left_csv),
        io.StringIO(right_csv),
        output,
        key="id",
        how="inner",
    )
    assert count == 0
    assert output.getvalue() == ""
