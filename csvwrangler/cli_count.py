import argparse
import csv
import sys

from csvwrangler.counter import count_file


def add_count_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("count", help="Count unique values in a column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file (or '-' for stdout)")
    p.add_argument("--column", required=True, help="Column to count values in")
    p.add_argument("--sort-by", choices=["count", "value"], default="count", help="Sort results by count or value")
    p.add_argument("--ascending", action="store_true", help="Sort in ascending order")


def run_count(args: argparse.Namespace) -> None:
    try:
        with open(args.input, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = ["value", "count"]
            if args.output == "-":
                writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
                count_file(reader, writer, column=args.column, sort_by=args.sort_by, ascending=args.ascending)
            else:
                with open(args.output, "w", newline="", encoding="utf-8") as out:
                    writer = csv.DictWriter(out, fieldnames=fieldnames)
                    count_file(reader, writer, column=args.column, sort_by=args.sort_by, ascending=args.ascending)
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
