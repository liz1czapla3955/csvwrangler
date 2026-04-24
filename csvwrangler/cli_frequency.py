"""CLI sub-command: frequency — value frequency table for a CSV column."""
import argparse
import csv
import sys

from csvwrangler.differ2 import frequency_file


def add_frequency_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "frequency",
        help="Count how often each value appears in a column.",
    )
    p.add_argument("input", nargs="?", default="-", help="Input CSV file (default: stdin)")
    p.add_argument("-o", "--output", default="-", help="Output CSV file (default: stdout)")
    p.add_argument("-c", "--column", required=True, help="Column to analyse")
    p.add_argument(
        "--output-column",
        default="frequency",
        metavar="NAME",
        help="Name for the count column (default: frequency)",
    )
    p.add_argument(
        "--sort-by",
        choices=["count", "value"],
        default="count",
        help="Sort output by count or value (default: count)",
    )
    p.add_argument(
        "--ascending",
        action="store_true",
        help="Sort in ascending order (default: descending)",
    )
    p.set_defaults(func=run_frequency)


def run_frequency(args: argparse.Namespace) -> None:
    in_fh = open(args.input, newline="") if args.input != "-" else sys.stdin
    out_fh = open(args.output, "w", newline="") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_fh)
        writer = csv.DictWriter(out_fh, fieldnames=[])
        try:
            frequency_file(
                reader,
                writer,
                column=args.column,
                output_column=args.output_column,
                sort_by=args.sort_by,
                ascending=args.ascending,
            )
        except KeyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
    finally:
        if args.input != "-":
            in_fh.close()
        if args.output != "-":
            out_fh.close()
