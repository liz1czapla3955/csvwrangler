import csv
import io


def annotate_rows(rows, conditions):
    """
    Annotate rows by adding a label column based on conditions.

    conditions: list of (column, op, value, label) tuples evaluated in order.
    The first matching condition wins. If no condition matches, label is ''.

    Supported ops: eq, ne, lt, gt, lte, gte, contains, startswith, endswith
    """
    ops = {
        'eq': lambda a, b: a == b,
        'ne': lambda a, b: a != b,
        'lt': lambda a, b: _num(a) < _num(b),
        'gt': lambda a, b: _num(a) > _num(b),
        'lte': lambda a, b: _num(a) <= _num(b),
        'gte': lambda a, b: _num(a) >= _num(b),
        'contains': lambda a, b: b in a,
        'startswith': lambda a, b: a.startswith(b),
        'endswith': lambda a, b: a.endswith(b),
    }

    for row in rows:
        label = ''
        for col, op, value, tag in conditions:
            cell = row.get(col, '')
            try:
                if ops[op](cell, value):
                    label = tag
                    break
            except (TypeError, ValueError):
                continue
        row = dict(row)
        row['_annotation'] = label
        yield row


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def annotate_file(reader, writer, conditions, output_column='_annotation'):
    rows = list(reader)
    if not rows:
        return
    annotated = list(annotate_rows(rows, conditions))
    fieldnames = list(rows[0].keys()) + ['_annotation']
    # rename if custom
    if output_column != '_annotation':
        annotated = [
            {**{k: v for k, v in r.items() if k != '_annotation'},
             output_column: r['_annotation']}
            for r in annotated
        ]
        fieldnames = list(rows[0].keys()) + [output_column]
    writer.writeheader(fieldnames)
    for row in annotated:
        writer.writerow(row)
