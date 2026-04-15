"""Tests for csvwrangler.aggregator."""

import csv
import os
import tempfile

import pytest

from csvwrangler.aggregator import aggregate_rows, aggregate_file


SAMPLE_ROWS = [
    {"dept": "eng", "name": "Alice", "salary": "90000"},
    {"dept": "eng", "name": "Bob", "salary": "80000"},
    {"dept": "hr", "name": "Carol", "salary": "70000"},
    {"dept": "hr", "name": "Dave", "salary": "72000"},
    {"dept": "eng", "name": "Eve", "salary": "95000"},
]


def _rows_as_dict(rows):
    return {r[list(r.keys())[0]]: r for r in rows}


def test_aggregate_count():
    result = aggregate_rows(SAMPLE_ROWS, group_by=["dept"], agg_column=None, agg_func="count")
    by_dept = {r["dept"]: int(r["count"]) for r in result}
    assert by_dept["eng"] == 3
    assert by_dept["hr"] == 2


def test_aggregate_sum():
    result = aggregate_rows(SAMPLE_ROWS, group_by=["dept"], agg_column="salary", agg_func="sum")
    by_dept = {r["dept"]: float(r["sum_salary"]) for r in result}
    assert by_dept["eng"] == pytest.approx(265000.0)
    assert by_dept["hr"] == pytest.approx(142000.0)


def test_aggregate_min():
    result = aggregate_rows(SAMPLE_ROWS, group_by=["dept"], agg_column="salary", agg_func="min")
    by_dept = {r["dept"]: float(r["min_salary"]) for r in result}
    assert by_dept["eng"] == pytest.approx(80000.0)
    assert by_dept["hr"] == pytest.approx(70000.0)


def test_aggregate_max():
    result = aggregate_rows(SAMPLE_ROWS, group_by=["dept"], agg_column="salary", agg_func="max")
    by_dept = {r["dept"]: float(r["max_salary"]) for r in result}
    assert by_dept["eng"] == pytest.approx(95000.0)
    assert by_dept["hr"] == pytest.approx(72000.0)


def test_aggregate_mean():
    result = aggregate_rows(SAMPLE_ROWS, group_by=["dept"], agg_column="salary", agg_func="mean")
    by_dept = {r["dept"]: float(r["mean_salary"]) for r in result}
    assert by_dept["eng"] == pytest.approx(265000 / 3)
    assert by_dept["hr"] == pytest.approx(71000.0)


def test_aggregate_unsupported_func():
    with pytest.raises(ValueError, match="Unsupported aggregation"):
        aggregate_rows(SAMPLE_ROWS, group_by=["dept"], agg_column="salary", agg_func="median")


def test_aggregate_missing_agg_col():
    with pytest.raises(ValueError, match="agg_column is required"):
        aggregate_rows(SAMPLE_ROWS, group_by=["dept"], agg_column=None, agg_func="sum")


def test_aggregate_missing_group_col():
    with pytest.raises(ValueError, match="Group-by column"):
        aggregate_rows(SAMPLE_ROWS, group_by=["nonexistent"], agg_column=None, agg_func="count")


def test_aggregate_non_numeric_value():
    rows = [{"dept": "eng", "salary": "not_a_number"}]
    with pytest.raises(ValueError, match="Non-numeric"):
        aggregate_rows(rows, group_by=["dept"], agg_column="salary", agg_func="sum")


def test_aggregate_multi_group_by():
    rows = [
        {"dept": "eng", "level": "senior", "salary": "100000"},
        {"dept": "eng", "level": "junior", "salary": "60000"},
        {"dept": "eng", "level": "senior", "salary": "110000"},
    ]
    result = aggregate_rows(rows, group_by=["dept", "level"], agg_column="salary", agg_func="count")
    counts = {(r["dept"], r["level"]): int(r["count"]) for r in result}
    assert counts[("eng", "senior")] == 2
    assert counts[("eng", "junior")] == 1


def test_aggregate_file(tmp_path):
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"

    with open(input_file, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["dept", "salary"])
        writer.writeheader()
        writer.writerows([
            {"dept": "eng", "salary": "90000"},
            {"dept": "hr", "salary": "70000"},
            {"dept": "eng", "salary": "80000"},
        ])

    count = aggregate_file(
        str(input_file), str(output_file), group_by=["dept"], agg_column="salary", agg_func="sum"
    )
    assert count == 2

    with open(output_file, newline="") as fh:
        rows = list(csv.DictReader(fh))
    by_dept = {r["dept"]: float(r["sum_salary"]) for r in rows}
    assert by_dept["eng"] == pytest.approx(170000.0)
    assert by_dept["hr"] == pytest.approx(70000.0)
