"""CLI subcommand: stack — vertically concatenate CSV files."""
import argparse
import csv
import sys
from typing import List

from csvwrangler.stacker import stack_rows


def add_stack_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "stack",
        help="Vertically stack (concatenate) two or more CSV files.",
    )
    p.add_argument(
        "inputs",
        nargs="+",
        metavar="FILE",
        help="Input CSV files to stack (use '-' for stdin, only once).",
    )
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout).")
    p.add_argument(
        "--fill",
        default="",
        metavar="VALUE",
        help="Fill value for missing columns (default: empty string).",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Error if column sets differ between sources.",
    )
    p.set_defaults(func=run_stack)


def run_stack(args: argparse.Namespace) -> None:
    sources = []
    handles = []
    try:
        for path in args.inputs:
            if path == "-":
                fh = sys.stdin
            else:
                fh = open(path, newline="", encoding="utf-8")
                handles.append(fh)
            sources.append(list(csv.DictReader(fh)))

        rows = stack_rows(sources, fill_value=args.fill, strict=args.strict)

        if not rows:
            return

        fieldnames = list(rows[0].keys())

        if args.output == "-":
            out_fh = sys.stdout
            writer = csv.DictWriter(out_fh, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        else:
            with open(args.output, "w", newline="", encoding="utf-8") as out_fh:
                writer = csv.DictWriter(out_fh, fieldnames=fieldnames, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        for fh in handles:
            fh.close()
