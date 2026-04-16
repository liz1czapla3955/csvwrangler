"""CLI subcommand for string operations."""

import argparse
import csv
import sys

from csvwrangler.stringops import stringops_rows


def add_stringops_subparser(subparsers) -> None:
    p = subparsers.add_parser("stringops", help="Apply string operations to a column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to apply operation to")
    p.add_argument(
        "--op",
        required=True,
        choices=["upper", "lower", "strip", "lstrip", "rstrip", "title", "replace", "prefix", "suffix", "zfill"],
        help="String operation to apply",
    )
    p.add_argument("--arg", default="", help="Argument for the operation (e.g. old:new for replace)")


def run_stringops(args: argparse.Namespace) -> None:
    try:
        with open(args.input, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            rows = list(
                stringops_rows(reader, column=args.column, op=args.op, arg=args.arg)
            )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
