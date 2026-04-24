"""CLI sub-command: interleave — alternate rows from two CSV files."""

import csv
import sys

from csvwrangler.interleaver import interleave_files


def add_interleave_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "interleave",
        help="Alternate rows from two CSV files (A, B, A, B, …).",
    )
    p.add_argument("file_a", help="First input CSV file.")
    p.add_argument("file_b", help="Second input CSV file.")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout).")
    p.add_argument(
        "--fill",
        action="store_true",
        help="Continue with remaining rows when one source is shorter.",
    )
    p.add_argument(
        "--fill-value",
        default="",
        dest="fill_value",
        help="Value used to pad shorter source when --fill is active (default: empty).",
    )


def run_interleave(args) -> None:
    try:
        fh_a = open(args.file_a, newline="", encoding="utf-8")
        fh_b = open(args.file_b, newline="", encoding="utf-8")
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    reader_a = csv.DictReader(fh_a)
    reader_b = csv.DictReader(fh_b)

    if args.output == "-":
        out_fh = sys.stdout
        close_out = False
    else:
        out_fh = open(args.output, "w", newline="", encoding="utf-8")
        close_out = True

    writer = csv.DictWriter(out_fh, fieldnames=[], extrasaction="ignore")

    try:
        interleave_files(
            reader_a,
            reader_b,
            writer,
            fill=args.fill,
            fill_value=args.fill_value,
        )
    finally:
        fh_a.close()
        fh_b.close()
        if close_out:
            out_fh.close()
