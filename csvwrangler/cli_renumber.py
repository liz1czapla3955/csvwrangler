"""CLI sub-command: renumber — add or reset a sequential index column."""

import argparse
import csv
import sys

from csvwrangler.renumberer import renumber_file


def add_renumber_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "renumber",
        help="Add or reset a sequential numeric index column.",
    )
    p.add_argument("input", nargs="?", default="-", help="Input CSV file (default: stdin).")
    p.add_argument("-o", "--output", default="-", help="Output CSV file (default: stdout).")
    p.add_argument("-c", "--column", default="id", help="Column name for the index (default: id).")
    p.add_argument("-s", "--start", type=int, default=1, help="Starting value (default: 1).")
    p.add_argument("-t", "--step", type=int, default=1, help="Step between values (default: 1).")
    p.add_argument(
        "--no-overwrite",
        dest="overwrite",
        action="store_false",
        default=True,
        help="Skip rows where the column already has a value.",
    )


def run_renumber(args: argparse.Namespace) -> None:
    in_stream = open(args.input, newline="") if args.input != "-" else sys.stdin
    out_stream = open(args.output, "w", newline="") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_stream)
        # fieldnames resolved after first read; renumber_file handles new column
        writer = csv.DictWriter(out_stream, fieldnames=[])  # populated inside
        renumber_file(
            reader,
            writer,
            column=args.column,
            start=args.start,
            step=args.step,
            overwrite=args.overwrite,
        )
    finally:
        if args.input != "-":
            in_stream.close()
        if args.output != "-":
            out_stream.close()
