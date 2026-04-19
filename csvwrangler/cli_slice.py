import argparse
import csv
import sys

from csvwrangler.slicer import slice_file


def add_slice_subparser(subparsers) -> None:
    p = subparsers.add_parser("slice", help="Slice rows by index range")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--start", type=int, default=0, help="Start index (default 0)")
    p.add_argument("--stop", type=int, default=None, help="Stop index (exclusive, default end)")
    p.add_argument("--step", type=int, default=1, help="Step (default 1)")


def run_slice(args: argparse.Namespace) -> None:
    if args.step == 0:
        print("Error: step cannot be zero", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.input, newline="", encoding="utf-8") as inf:
            reader = csv.DictReader(inf)
            rows = list(reader)
            fieldnames = reader.fieldnames or []

        sliced = []
        if rows:
            from csvwrangler.slicer import slice_rows
            sliced = slice_rows(rows, start=args.start, stop=args.stop, step=args.step)

        with open(args.output, "w", newline="", encoding="utf-8") as outf:
            writer = csv.DictWriter(outf, fieldnames=fieldnames)
            writer.writeheader()
            for row in sliced:
                writer.writerow(row)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
