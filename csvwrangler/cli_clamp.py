"""CLI sub-command: clamp — clamp a numeric column to [low, high] bounds."""

from __future__ import annotations

import csv
import sys

from csvwrangler.clamper import clamp_file


def add_clamp_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "clamp",
        help="Clamp a numeric column to a fixed or percentile-based range.",
    )
    p.add_argument("input", help="Input CSV file (use '-' for stdin)")
    p.add_argument("-o", "--output", default="-", help="Output CSV file (default: stdout)")
    p.add_argument("-c", "--column", required=True, help="Column to clamp")
    p.add_argument("--low", type=float, default=None, help="Absolute lower bound")
    p.add_argument("--high", type=float, default=None, help="Absolute upper bound")
    p.add_argument("--low-pct", type=float, default=None, dest="low_pct",
                   help="Lower bound as percentile (0-100) computed from data")
    p.add_argument("--high-pct", type=float, default=None, dest="high_pct",
                   help="Upper bound as percentile (0-100) computed from data")
    p.add_argument("--output-column", default=None,
                   help="Write clamped values to this column instead of overwriting")
    p.set_defaults(func=run_clamp)


def run_clamp(args) -> None:
    in_fh = sys.stdin if args.input == "-" else open(args.input, newline="", encoding="utf-8")
    out_fh = sys.stdout if args.output == "-" else open(args.output, "w", newline="", encoding="utf-8")

    try:
        reader = csv.DictReader(in_fh)
        if reader.fieldnames is None:
            # peek to populate fieldnames
            first = next(iter(reader), None)
            if first is None:
                return

        fieldnames = list(reader.fieldnames or [])
        out_col = args.output_column or args.column
        if out_col not in fieldnames:
            fieldnames = fieldnames + [out_col]

        writer = csv.DictWriter(out_fh, fieldnames=fieldnames, extrasaction="ignore")

        clamp_file(
            reader=reader,
            writer=writer,
            column=args.column,
            low=args.low,
            high=args.high,
            low_pct=args.low_pct,
            high_pct=args.high_pct,
            output_column=args.output_column,
        )
    finally:
        if in_fh is not sys.stdin:
            in_fh.close()
        if out_fh is not sys.stdout:
            out_fh.close()
