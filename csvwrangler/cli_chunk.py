"""CLI sub-command: chunk — split CSV into fixed-size row chunks."""

import argparse
import csv
import sys

from csvwrangler.chunker import chunk_rows


def add_chunk_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "chunk",
        help="Output a specific fixed-size chunk of rows from a CSV file.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("-n", "--size", type=int, required=True,
                   help="Number of rows per chunk.")
    p.add_argument("-i", "--index", type=int, default=0,
                   help="0-based chunk index to output (default: 0).")
    p.add_argument("-o", "--output", default="-",
                   help="Output file (default: stdout).")
    p.set_defaults(func=run_chunk)


def run_chunk(args: argparse.Namespace) -> None:
    in_fh = sys.stdin if args.input == "-" else open(args.input, newline="")
    out_fh = sys.stdout if args.output == "-" else open(args.output, "w", newline="")

    try:
        reader = csv.DictReader(in_fh)
        rows = list(reader)
        if not rows:
            return

        try:
            chunks = list(chunk_rows(rows, args.size))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)

        if args.index >= len(chunks):
            print(
                f"error: chunk index {args.index} out of range "
                f"(file has {len(chunks)} chunk(s))",
                file=sys.stderr,
            )
            sys.exit(1)

        fieldnames = reader.fieldnames or []
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in chunks[args.index]:
            writer.writerow(row)
    finally:
        if in_fh is not sys.stdin:
            in_fh.close()
        if out_fh is not sys.stdout:
            out_fh.close()
