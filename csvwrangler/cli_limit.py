import argparse
import csv
import sys

from csvwrangler.limiter import limit_file


def add_limit_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "limit",
        help="Return a limited number of rows with an optional offset.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--limit", "-n",
        type=int,
        required=True,
        help="Maximum number of rows to output",
    )
    p.add_argument(
        "--offset", "-s",
        type=int,
        default=0,
        help="Number of rows to skip before starting output (default: 0)",
    )


def run_limit(args: argparse.Namespace) -> None:
    if args.limit < 0:
        print("Error: --limit must be non-negative", file=sys.stderr)
        sys.exit(1)
    if args.offset < 0:
        print("Error: --offset must be non-negative", file=sys.stderr)
        sys.exit(1)

    with open(args.input, newline="", encoding="utf-8") as inf, \
         open(args.output, "w", newline="", encoding="utf-8") as outf:
        reader = csv.DictReader(inf)
        if reader.fieldnames is None:
            return
        writer = csv.DictWriter(outf, fieldnames=reader.fieldnames)
        limit_file(reader, writer, limit=args.limit, offset=args.offset)
