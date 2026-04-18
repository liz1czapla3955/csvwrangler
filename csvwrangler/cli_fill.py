"""CLI subcommand: fill — fill missing CSV values."""
import argparse
import csv
import sys

from csvwrangler.filler import fill_file


def add_fill_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("fill", help="Fill missing values in CSV columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--columns", nargs="+", default=[], metavar="COL",
        help="Columns to fill (default: all)"
    )
    p.add_argument(
        "--method", choices=["value", "mean", "ffill"], default="value",
        help="Fill method (default: value)"
    )
    p.add_argument(
        "--fill-value", default="", dest="fill_value",
        help="Constant fill value when method=value (default: empty string)"
    )


def run_fill(args: argparse.Namespace) -> None:
    try:
        with open(args.input, newline="", encoding="utf-8") as in_f:
            reader = csv.DictReader(in_f)
            if reader.fieldnames is None:
                print("Error: empty input file", file=sys.stderr)
                sys.exit(1)
            with open(args.output, "w", newline="", encoding="utf-8") as out_f:
                writer = csv.DictWriter(out_f, fieldnames=reader.fieldnames)
                fill_file(
                    reader,
                    writer,
                    columns=args.columns,
                    method=args.method,
                    fill_value=args.fill_value,
                )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
