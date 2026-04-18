import pytest
from csvwrangler.binner import bin_rows


ROWS = [
    {"name": "a", "score": "5"},
    {"name": "b", "score": "15"},
    {"name": "c", "score": "25"},
    {"name": "d", "score": "35"},
    {"name": "e", "score": "-5"},
]


def test_bin_rows_default_labels():
    result = bin_rows(ROWS, "score", [0, 10, 20, 30])
    labels = [r["bin"] for r in result]
    assert labels == ["0-10", "10-20", "20-30", ">=30", "<0"]


def test_bin_rows_custom_labels():
    result = bin_rows(
        ROWS, "score", [0, 10, 20, 30], labels=["neg", "low", "mid", "high", "very_high"]
    )
    labels = [r["bin"] for r in result]
    assert labels == ["low", "mid", "high", "very_high", "neg"]


def test_bin_rows_custom_output_column():
    result = bin_rows(ROWS[:1], "score", [0, 10], output_column="category")
    assert "category" in result[0]
    assert "bin" not in result[0]


def test_bin_rows_non_numeric_passthrough():
    rows = [{"name": "x", "score": "n/a"}]
    result = bin_rows(rows, "score", [0, 10])
    assert result[0]["bin"] == ""


def test_bin_rows_missing_column_passthrough():
    rows = [{"name": "x"}]
    result = bin_rows(rows, "score", [0, 10])
    assert result[0]["bin"] == ""


def test_bin_rows_empty_bins():
    rows = [{"name": "a", "score": "42"}]
    result = bin_rows(rows, "score", [], labels=["everything"])
    assert result[0]["bin"] == "everything"


def test_bin_rows_wrong_label_count_raises():
    with pytest.raises(ValueError, match="labels"):
        bin_rows(ROWS, "score", [0, 10], labels=["only_two", "labels"])


def test_bin_rows_boundary_is_lower_inclusive():
    rows = [{"name": "a", "score": "10"}]
    result = bin_rows(rows, "score", [0, 10, 20])
    assert result[0]["bin"] == "10-20"


def test_bin_rows_preserves_other_fields():
    rows = [{"name": "alice", "score": "5", "dept": "eng"}]
    result = bin_rows(rows, "score", [0, 10])
    assert result[0]["name"] == "alice"
    assert result[0]["dept"] == "eng"


def test_bin_rows_empty_input():
    result = bin_rows([], "score", [0, 10])
    assert result == []
