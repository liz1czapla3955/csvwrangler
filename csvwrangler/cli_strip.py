"""CLI subcommand: strip — remove blank/comment/head/tail rows from a CSV."""

import argparse
import csv
import sys

from csvwrangler.stripper import strip_file


def add_strip_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "strip",
        help="Remove blank rows, comment rows, or N rows from head/tail.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("-o", "--output", default="-", help="Output CSV file (default: stdout).")
    p.add_argument(
        "--no-strip-blank",
        action="store_true",
        default=False,
        help="Do not remove rows where all values are empty.",
    )
    p.add_argument(
        "--comment-prefix",
        default=None,
        metavar="PREFIX",
        help="Remove rows whose first column starts with PREFIX (e.g. '#').",
    )
    p.add_argument(
        "--head",
        type=int,
        default=0,
        metavar="N",
        help="Strip N rows from the start of the file.",
    )
    p.add_argument(
        "--tail",
        type=int,
        default=0,
        metavar="N",
        help="Strip N rows from the end of the file.",
    )
    p.set_defaults(func=run_strip)


def run_strip(args: argparse.Namespace) -> None:
    in_fh = open(args.input, newline="") if args.input != "-" else sys.stdin
    out_fh = open(args.output, "w", newline="") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_fh)
        if reader.fieldnames is None:
            # Empty file — nothing to do.
            return

        writer = csv.DictWriter(out_fh, fieldnames=reader.fieldnames)
        strip_file(
            reader,
            writer,
            strip_blank=not args.no_strip_blank,
            comment_prefix=args.comment_prefix,
            head=args.head,
            tail=args.tail,
        )
    finally:
        if args.input != "-":
            in_fh.close()
        if args.output != "-":
            out_fh.close()
