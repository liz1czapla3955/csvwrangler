"""CLI subcommand: offset — shift numeric column values."""

import argparse
import csv
import sys

from csvwrangler.offsetter import offset_file


def add_offset_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'offset' subcommand."""
    parser = subparsers.add_parser(
        "offset",
        help="Shift numeric column values by a fixed amount or percentage.",
    )
    parser.add_argument(
        "input",
        help="Input CSV file (use '-' for stdin).",
    )
    parser.add_argument(
        "-o", "--output",
        default="-",
        help="Output CSV file (default: stdout).",
    )
    parser.add_argument(
        "-c", "--columns",
        required=True,
        help="Comma-separated list of columns to offset.",
    )
    parser.add_argument(
        "-a", "--amount",
        type=float,
        required=True,
        help="Amount to add to each value (can be negative).",
    )
    parser.add_argument(
        "-p", "--percent",
        action="store_true",
        default=False,
        help="Treat --amount as a percentage of the original value.",
    )
    parser.set_defaults(func=run_offset)


def run_offset(args: argparse.Namespace) -> None:
    """Execute the offset subcommand."""
    columns = [c.strip() for c in args.columns.split(",")]

    in_stream = open(args.input, newline="") if args.input != "-" else sys.stdin
    out_stream = open(args.output, "w", newline="") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_stream)
        if not reader.fieldnames:
            sys.exit("error: input CSV has no headers")
        writer = csv.DictWriter(out_stream, fieldnames=reader.fieldnames)
        offset_file(reader, writer, columns, args.amount, args.percent)
    finally:
        if args.input != "-":
            in_stream.close()
        if args.output != "-":
            out_stream.close()
