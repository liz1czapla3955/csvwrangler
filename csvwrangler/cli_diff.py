"""CLI sub-command: diff — compare two CSV files by key fields."""

import argparse
import sys

from csvwrangler.differ import diff_files


def add_diff_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "diff",
        help="Compare two CSV files and show added, removed, or changed rows.",
    )
    parser.add_argument("file_a", help="First (original) CSV file")
    parser.add_argument("file_b", help="Second (new) CSV file")
    parser.add_argument(
        "--key",
        required=True,
        nargs="+",
        metavar="FIELD",
        help="One or more fields to use as the row identity key",
    )
    parser.add_argument(
        "--include-unchanged",
        action="store_true",
        default=False,
        help="Also output rows that are identical in both files",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="-",
        help="Output file path (default: stdout)",
    )
    parser.set_defaults(func=run_diff)


def run_diff(args: argparse.Namespace) -> None:
    if args.output == "-":
        out = sys.stdout
        diff_files(
            args.file_a,
            args.file_b,
            args.key,
            out,
            include_unchanged=args.include_unchanged,
        )
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as out:
            diff_files(
                args.file_a,
                args.file_b,
                args.key,
                out,
                include_unchanged=args.include_unchanged,
            )
