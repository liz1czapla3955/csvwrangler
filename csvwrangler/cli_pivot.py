"""CLI sub-command: pivot"""

import argparse
import csv
import sys

from csvwrangler.pivotter import pivot_file


def add_pivot_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "pivot",
        help="Pivot a CSV: spread one column's values as headers and aggregate another.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("--index", required=True, help="Column to use as the row identifier.")
    p.add_argument("--columns", required=True, help="Column whose values become new headers.")
    p.add_argument("--values", required=True, help="Column whose values are aggregated.")
    p.add_argument(
        "--aggfunc",
        default="sum",
        choices=["sum", "count", "min", "max", "first"],
        help="Aggregation function to apply (default: sum).",
    )
    p.add_argument("-o", "--output", default="-", help="Output CSV file (default: stdout).")
    p.set_defaults(func=run_pivot)


def run_pivot(args: argparse.Namespace) -> None:
    in_stream = open(args.input, newline="") if args.input != "-" else sys.stdin
    out_stream = open(args.output, "w", newline="") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_stream)
        try:
            pivoted = pivot_file(
                reader,
                index=args.index,
                columns=args.columns,
                values=args.values,
                aggfunc=args.aggfunc,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

        if not pivoted:
            return

        fieldnames = list(pivoted[0].keys())
        writer = csv.DictWriter(out_stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pivoted)
    finally:
        if args.input != "-":
            in_stream.close()
        if args.output != "-":
            out_stream.close()
