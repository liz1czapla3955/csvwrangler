"""Tests for csvwrangler.sampler."""

import pytest

from csvwrangler.sampler import sample_rows


ROWS = [
    {"id": "1", "name": "Alice"},
    {"id": "2", "name": "Bob"},
    {"id": "3", "name": "Carol"},
    {"id": "4", "name": "Dave"},
    {"id": "5", "name": "Eve"},
]


def test_sample_first():
    result = sample_rows(ROWS, 3, mode="first")
    assert result == ROWS[:3]


def test_sample_last():
    result = sample_rows(ROWS, 2, mode="last")
    assert result == ROWS[-2:]


def test_sample_last_zero():
    result = sample_rows(ROWS, 0, mode="last")
    assert result == []


def test_sample_random_count():
    result = sample_rows(ROWS, 3, mode="random", seed=42)
    assert len(result) == 3


def test_sample_random_reproducible():
    r1 = sample_rows(ROWS, 4, mode="random", seed=7)
    r2 = sample_rows(ROWS, 4, mode="random", seed=7)
    assert r1 == r2


def test_sample_random_different_seeds():
    r1 = sample_rows(ROWS, 4, mode="random", seed=1)
    r2 = sample_rows(ROWS, 4, mode="random", seed=99)
    # Very unlikely to be equal with different seeds on 5 rows choose 4
    # but not guaranteed; just check they are valid samples
    assert len(r1) == 4
    assert len(r2) == 4


def test_sample_n_larger_than_rows():
    result = sample_rows(ROWS, 100, mode="random", seed=0)
    assert len(result) == len(ROWS)


def test_sample_first_n_larger_than_rows():
    result = sample_rows(ROWS, 100, mode="first")
    assert result == ROWS


def test_sample_negative_n_raises():
    with pytest.raises(ValueError, match="non-negative"):
        sample_rows(ROWS, -1)


def test_sample_invalid_mode_raises():
    with pytest.raises(ValueError, match="Unknown sampling mode"):
        sample_rows(ROWS, 2, mode="middle")


def test_sample_empty_rows():
    result = sample_rows([], 5, mode="random", seed=0)
    assert result == []


def test_sample_zero_n_first():
    result = sample_rows(ROWS, 0, mode="first")
    assert result == []
