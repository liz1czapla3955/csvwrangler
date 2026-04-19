import pytest
from csvwrangler.annotator import annotate_rows, _num


def _rows():
    return [
        {'name': 'Alice', 'score': '92', 'city': 'Berlin'},
        {'name': 'Bob', 'score': '45', 'city': 'Paris'},
        {'name': 'Carol', 'score': '70', 'city': 'Berlin'},
        {'name': 'Dave', 'score': '10', 'city': 'Rome'},
    ]


def test_annotate_eq_match():
    conditions = [('city', 'eq', 'Berlin', 'german')]
    result = list(annotate_rows(_rows(), conditions))
    assert result[0]['_annotation'] == 'german'
    assert result[1]['_annotation'] == ''


def test_annotate_gt_match():
    conditions = [('score', 'gt', '80', 'high')]
    result = list(annotate_rows(_rows(), conditions))
    assert result[0]['_annotation'] == 'high'
    assert result[1]['_annotation'] == ''


def test_annotate_lte_match():
    conditions = [('score', 'lte', '45', 'low')]
    result = list(annotate_rows(_rows(), conditions))
    assert result[1]['_annotation'] == 'low'
    assert result[3]['_annotation'] == 'low'
    assert result[0]['_annotation'] == ''


def test_annotate_first_condition_wins():
    conditions = [
        ('score', 'gt', '80', 'high'),
        ('score', 'gt', '60', 'medium'),
    ]
    result = list(annotate_rows(_rows(), conditions))
    assert result[0]['_annotation'] == 'high'
    assert result[2]['_annotation'] == 'medium'
    assert result[1]['_annotation'] == ''


def test_annotate_contains():
    conditions = [('city', 'contains', 'er', 'has_er')]
    result = list(annotate_rows(_rows(), conditions))
    assert result[0]['_annotation'] == 'has_er'  # Berlin
    assert result[1]['_annotation'] == ''


def test_annotate_startswith():
    conditions = [('name', 'startswith', 'A', 'a_name')]
    result = list(annotate_rows(_rows(), conditions))
    assert result[0]['_annotation'] == 'a_name'
    assert result[1]['_annotation'] == ''


def test_annotate_endswith():
    conditions = [('name', 'endswith', 'e', 'ends_e')]
    result = list(annotate_rows(_rows(), conditions))
    assert result[0]['_annotation'] == 'ends_e'  # Alice
    assert result[3]['_annotation'] == 'ends_e'  # Dave
    assert result[1]['_annotation'] == ''


def test_annotate_no_conditions():
    result = list(annotate_rows(_rows(), []))
    for row in result:
        assert row['_annotation'] == ''


def test_annotate_missing_column_skips():
    conditions = [('nonexistent', 'eq', 'x', 'found')]
    result = list(annotate_rows(_rows(), conditions))
    for row in result:
        assert row['_annotation'] == ''


def test_annotate_preserves_original_fields():
    conditions = [('score', 'gt', '50', 'pass')]
    result = list(annotate_rows(_rows(), conditions))
    assert result[0]['name'] == 'Alice'
    assert result[0]['score'] == '92'
    assert result[0]['city'] == 'Berlin'


def test_num_valid():
    assert _num('3.5') == 3.5


def test_num_invalid_returns_zero():
    assert _num('abc') == 0.0
