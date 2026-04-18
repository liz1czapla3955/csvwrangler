"""CLI subcommand for column comparison."""
import csv
import sys
from csvwrangler.comparer import compare_file


def add_compare_subparser(subparsers):
    p = subparsers.add_parser("compare", help="Compare two columns and flag the result")
    p.add_argument("input", help="Input CSV file (use - for stdin)")
    p.add_argument("--col-a", required=True, help="First column")
    p.add_argument("--col-b", required=True, help="Second column")
    p.add_argument(
        "--op",
        required=True,
        choices=["eq", "ne", "lt", "le", "gt", "ge"],
        help="Comparison operator",
    )
    p.add_argument("--output-col", default="match", help="Name of the output flag column")
    p.add_argument("--true-val", default="true", help="Value when comparison is true")
    p.add_argument("--false-val", default="false", help="Value when comparison is false")
    p.add_argument("--output", default="-", help="Output CSV file (use - for stdout)")
    p.set_defaults(func=run_compare)


def run_compare(args):
    in_fh = open(args.input) if args.input != "-" else sys.stdin
    out_fh = open(args.output, "w", newline="") if args.output != "-" else sys.stdout
    try:
        reader = csv.DictReader(in_fh)
        rows = list(reader)
        if not rows:
            return
        fieldnames = list(rows[0].keys())
        if args.output_col not in fieldnames:
            fieldnames = fieldnames + [args.output_col]
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        compare_file(
            iter(rows), writer,
            args.col_a, args.col_b, args.op,
            args.output_col, args.true_val, args.false_val,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if args.input != "-":
            in_fh.close()
        if args.output != "-":
            out_fh.close()
