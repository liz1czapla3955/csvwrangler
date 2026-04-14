"""Tests for schema inference module."""

import csv
import os
import tempfile

import pytest

from csvwrangler.schema_inferrer import (
    _infer_type,
    _resolve_types,
    format_schema,
    infer_schema,
)


# --- _infer_type ---

def test_infer_type_integer():
    assert _infer_type('42') == 'integer'


def test_infer_type_float():
    assert _infer_type('3.14') == 'float'


def test_infer_type_boolean():
    assert _infer_type('true') == 'boolean'
    assert _infer_type('False') == 'boolean'
    assert _infer_type('yes') == 'boolean'


def test_infer_type_date_iso():
    assert _infer_type('2024-01-15') == ' test_infer_type_date_slash():
    assert _infer_type('15/01/2024') == 'date'


def test_infer_type_string():
    assert _infer_type('hello world') == 'string'


def test_infer_type_empty():
    assert _infer_type('') == 'empty'
    assert _infer_type('   ') == 'empty'


# --- _resolve_types ---

def test_resolve_types_single():
    assert _resolve_types(['integer', 'integer']) == 'integer'


def test_resolve_types_int_float_becomes_float():
    assert _resolve_types(['integer', 'float']) == 'float'


def test_resolve_types_mixed_becomes_string():
    assert _resolve_types(['integer', 'string']) == 'string'


def test_resolve_types_all_empty_becomes_string():
    assert _resolve_types(['empty', 'empty']) == 'string'


def test_resolve_types_empty_ignored():
    assert _resolve_types(['empty', 'integer']) == 'integer'


# --- infer_schema ---

def _write_csv(rows, header):
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='')
    writer = csv.DictWriter(tmp, fieldnames=header)
    writer.writeheader()
    writer.writerows(rows)
    tmp.close()
    return tmp.name


def test_infer_schema_basic():
    path = _write_csv(
        [{'name': 'Alice', 'age': '30', 'score': '9.5'},
         {'name': 'Bob', 'age': '25', 'score': '8.0'}],
        header=['name', 'age', 'score'],
    )
    try:
        schema = infer_schema(path)
        assert schema['name'] == 'string'
        assert schema['age'] == 'integer'
        assert schema['score'] == 'float'
    finally:
        os.unlink(path)


def test_infer_schema_respects_sample_size():
    rows = [{'val': str(i)} for i in range(200)]
    path = _write_csv(rows, header=['val'])
    try:
        schema = infer_schema(path, sample_size=10)
        assert schema['val'] == 'integer'
    finally:
        os.unlink(path)


def test_infer_schema_file_not_found():
    with pytest.raises(FileNotFoundError):
        infer_schema('/nonexistent/path/file.csv')


# --- format_schema ---

def test_format_schema_contains_columns():
    schema = {'id': 'integer', 'name': 'string'}
    output = format_schema(schema)
    assert 'id' in output
    assert 'integer' in output
    assert 'name' in output
    assert 'string' in output


def test_format_schema_empty():
    assert format_schema({}) == '(no columns detected)'
