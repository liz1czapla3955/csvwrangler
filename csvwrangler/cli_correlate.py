"""CLI subcommand: correlate — compute pairwise Pearson correlations."""

from __future__ import annotations

import argparse
import csv
import sys

from csvwrangler.correlator import correlate_file


def add_correlate_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "correlate",
        help="Compute pairwise Pearson correlations between numeric columns.",
    )
    p.add_argument("input", nargs="?", default="-", help="Input CSV (default: stdin)")
    p.add_argument("-o", "--output", default="-", help="Output CSV (default: stdout)")
    p.add_argument(
        "-c",
        "--columns",
        required=True,
        help="Comma-separated list of numeric columns to correlate.",
    )
    p.add_argument(
        "-d",
        "--decimals",
        type=int,
        default=4,
        help="Decimal places for correlation values (default: 4).",
    )
    p.set_defaults(func=run_correlate)


def run_correlate(args: argparse.Namespace) -> None:
    columns = [c.strip() for c in args.columns.split(",") if c.strip()]
    if not columns:
        print("error: --columns must specify at least one column.", file=sys.stderr)
        sys.exit(1)

    in_stream = open(args.input, newline="") if args.input != "-" else sys.stdin
    out_stream = open(args.output, "w", newline="") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_stream)
        writer = csv.DictWriter(out_stream, fieldnames=["column"] + columns)
        correlate_file(reader, writer, columns=columns, decimals=args.decimals)
    finally:
        if args.input != "-":
            in_stream.close()
        if args.output != "-":
            out_stream.close()
