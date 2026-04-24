import pytest
from csvwrangler.ranker import rank_rows


ROWS = [
    {"name": "Alice", "score": "90"},
    {"name": "Bob", "score": "85"},
    {"name": "Carol", "score": "90"},
    {"name": "Dave", "score": "70"},
]


def test_rank_dense_ascending():
    result = rank_rows(ROWS, "score", method="dense", ascending=True)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["Dave"] == "1"
    assert ranks["Bob"] == "2"
    assert ranks["Alice"] == ranks["Carol"] == "3"


def test_rank_dense_descending():
    result = rank_rows(ROWS, "score", method="dense", ascending=False)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["Alice"] == ranks["Carol"] == "1"
    assert ranks["Bob"] == "2"
    assert ranks["Dave"] == "3"


def test_rank_standard_ascending():
    result = rank_rows(ROWS, "score", method="standard", ascending=True)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["Dave"] == "1"
    assert ranks["Bob"] == "2"
    # Alice and Carol both get rank 3, next would be 5 (skipped 4)
    assert ranks["Alice"] == ranks["Carol"] == "3"


def test_rank_standard_descending():
    result = rank_rows(ROWS, "score", method="standard", ascending=False)
    ranks = {r["name"]: r["rank"] for r in result}
    # Alice and Carol both get rank 1, next would be 3 (skipped 2)
    assert ranks["Alice"] == ranks["Carol"] == "1"
    assert ranks["Bob"] == "3"
    assert ranks["Dave"] == "4"


def test_rank_row_method_unique():
    result = rank_rows(ROWS, "score", method="row", ascending=False)
    rank_values = [r["rank"] for r in result]
    assert len(set(rank_values)) == 4  # all unique


def test_rank_custom_column_name():
    result = rank_rows(ROWS, "score", rank_column="position")
    assert "position" in result[0]
    assert "rank" not in result[0]


def test_rank_preserves_original_columns():
    result = rank_rows(ROWS, "score")
    for row in result:
        assert "name" in row
        assert "score" in row
        assert "rank" in row


def test_rank_empty_input():
    result = rank_rows([], "score")
    assert result == []


def test_rank_missing_column_raises():
    with pytest.raises(ValueError, match="Column 'missing'"):
        rank_rows(ROWS, "missing")


def test_rank_invalid_method_raises():
    with pytest.raises(ValueError, match="Unknown rank method"):
        rank_rows(ROWS, "score", method="bogus")


def test_rank_string_values():
    rows = [
        {"name": "banana"},
        {"name": "apple"},
        {"name": "cherry"},
    ]
    result = rank_rows(rows, "name", method="dense", ascending=True)
    ranks = {r["name"]: r["rank"] for r in result}
    assert ranks["apple"] == "1"
    assert ranks["banana"] == "2"
    assert ranks["cherry"] == "3"
