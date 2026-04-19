import sys
import csv
from csvwrangler.annotator import annotate_rows


def add_annotate_subparser(subparsers):
    p = subparsers.add_parser('annotate', help='Annotate rows with labels based on conditions')
    p.add_argument('input', help='Input CSV file')
    p.add_argument('output', help='Output CSV file')
    p.add_argument(
        '--condition', metavar='COL:OP:VALUE:LABEL',
        action='append', dest='conditions', default=[],
        help='Condition in format col:op:value:label (repeatable)'
    )
    p.add_argument('--output-column', default='_annotation', help='Name of the annotation column')
    return p


def run_annotate(args):
    conditions = []
    for raw in args.conditions:
        parts = raw.split(':', 3)
        if len(parts) != 4:
            print(f"Invalid condition: {raw}", file=sys.stderr)
            sys.exit(1)
        col, op, value, label = parts
        conditions.append((col, op, value, label))

    try:
        with open(args.input, newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return
            fieldnames = list(rows[0].keys())

        annotated = list(annotate_rows(rows, conditions))
        out_col = args.output_column
        out_fieldnames = fieldnames + [out_col]

        with open(args.output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames, extrasaction='ignore')
            writer.writeheader()
            for row in annotated:
                out_row = {k: row.get(k, '') for k in fieldnames}
                out_row[out_col] = row.get('_annotation', '')
                writer.writerow(out_row)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
