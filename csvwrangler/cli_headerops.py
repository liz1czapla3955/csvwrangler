"""CLI subcommand for header operations."""
from __future__ import annotations
import argparse
import csv
import sys

from csvwrangler.headerops import headerops_file


def add_headerops_subparser(subparsers) -> None:
    p = subparsers.add_parser("headerops", help="Reorder, drop, or insert columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--op",
        choices=["reorder", "drop", "insert"],
        required=True,
        help="Operation to perform",
    )
    p.add_argument("--columns", nargs="+", help="Column names (reorder/drop)")
    p.add_argument("--insert-name", help="Name of column to insert")
    p.add_argument("--insert-value", default="", help="Default value for inserted column")
    p.add_argument("--insert-position", type=int, default=-1, help="Position to insert column")
    p.set_defaults(func=run_headerops)


def run_headerops(args: argparse.Namespace) -> None:
    try:
        with open(args.input, newline="") as inf, open(args.output, "w", newline="") as outf:
            reader = csv.DictReader(inf)
            rows = list(reader)
            if not rows:
                return
            # determine fieldnames after operation for writer
            import io
            from csvwrangler.headerops import reorder_columns, drop_columns, insert_column
            if args.op == "reorder":
                result = list(reorder_columns(rows, args.columns or []))
            elif args.op == "drop":
                result = list(drop_columns(rows, args.columns or []))
            else:
                result = list(insert_column(rows, args.insert_name or "new",
                                            args.insert_value, args.insert_position))
            if result:
                writer = csv.DictWriter(outf, fieldnames=list(result[0].keys()))
                writer.writeheader()
                writer.writerows(result)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
