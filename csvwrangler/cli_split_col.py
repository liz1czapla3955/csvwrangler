"""CLI sub-command: split-col — split a column into multiple columns."""
import argparse
import csv
import sys

from csvwrangler.splitter_col import split_column_rows


def add_split_col_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "split-col",
        help="Split a column into multiple columns by a delimiter",
    )
    p.add_argument("input", help="Input CSV file (use - for stdin)")
    p.add_argument("--column", required=True, help="Column to split")
    p.add_argument("--delimiter", default=",", help="Delimiter to split on (default: ,)")
    p.add_argument(
        "--output-columns",
        dest="output_columns",
        help="Comma-separated names for the output columns",
    )
    p.add_argument(
        "--max-split",
        dest="max_split",
        type=int,
        default=-1,
        help="Maximum number of splits (-1 = unlimited)",
    )
    p.set_defaults(func=run_split_col)


def run_split_col(args: argparse.Namespace) -> None:
    in_fh = open(args.input) if args.input != "-" else sys.stdin
    try:
        reader = csv.DictReader(in_fh)
        rows = list(reader)
        if not rows:
            return

        output_columns = (
            [c.strip() for c in args.output_columns.split(",")]
            if args.output_columns
            else None
        )

        result = list(
            split_column_rows(
                rows,
                args.column,
                args.delimiter,
                output_columns,
                args.max_split,
            )
        )
        if not result:
            return

        writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
        writer.writeheader()
        for row in result:
            writer.writerow(row)
    finally:
        if args.input != "-":
            in_fh.close()
