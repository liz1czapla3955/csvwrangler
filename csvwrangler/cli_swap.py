"""CLI sub-command: swap — exchange the values of two CSV columns."""

import argparse
import csv
import sys

from csvwrangler.swapper import swap_file


def add_swap_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "swap",
        help="Exchange the values of two columns in every row.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument(
        "--col-a",
        required=True,
        metavar="COL_A",
        help="First column name.",
    )
    p.add_argument(
        "--col-b",
        required=True,
        metavar="COL_B",
        help="Second column name.",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="Output file (default: stdout).",
    )
    p.set_defaults(func=run_swap)


def run_swap(args: argparse.Namespace) -> None:
    in_fh = sys.stdin if args.input == "-" else open(args.input, newline="")
    try:
        reader = csv.DictReader(in_fh)
        fieldnames = list(reader.fieldnames or [])

        if args.col_a not in fieldnames or args.col_b not in fieldnames:
            missing = [
                c for c in (args.col_a, args.col_b) if c not in fieldnames
            ]
            print(
                f"swap: column(s) not found: {', '.join(missing)}",
                file=sys.stderr,
            )
            sys.exit(1)

        out_fh = (
            open(args.output, "w", newline="")
            if args.output
            else sys.stdout
        )
        try:
            writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
            swap_file(reader, writer, args.col_a, args.col_b)
        finally:
            if args.output:
                out_fh.close()
    finally:
        if args.input != "-":
            in_fh.close()
