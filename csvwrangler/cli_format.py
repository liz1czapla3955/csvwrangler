"""CLI subcommand: format — reformat values in a CSV column."""
import csv
import sys
import argparse

from csvwrangler.formatter import format_file


def add_format_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("format", help="Reformat values in a column")
    p.add_argument("input", help="Input CSV file (use - for stdin)")
    p.add_argument("output", help="Output CSV file (use - for stdout)")
    p.add_argument("--column", required=True, help="Column to format")
    p.add_argument(
        "--type",
        dest="fmt_type",
        required=True,
        choices=["date", "number", "zeropad", "upper", "lower", "title"],
        help="Format type",
    )
    p.add_argument(
        "--arg",
        dest="fmt_arg",
        default="",
        help="Format argument (e.g. date: '%%Y-%%m-%%d->%%d/%%m/%%Y', number: '.2f', zeropad: '5')",
    )


def run_format(args: argparse.Namespace) -> None:
    in_f = open(args.input, newline="", encoding="utf-8") if args.input != "-" else sys.stdin
    out_f = open(args.output, "w", newline="", encoding="utf-8") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_f)
        if not reader.fieldnames:
            print("Error: empty input", file=sys.stderr)
            sys.exit(1)

        if args.column not in reader.fieldnames:
            print(f"Error: column '{args.column}' not found", file=sys.stderr)
            sys.exit(1)

        writer = csv.DictWriter(out_f, fieldnames=reader.fieldnames)
        format_file(reader, writer, args.column, args.fmt_type, args.fmt_arg)
    finally:
        if args.input != "-":
            in_f.close()
        if args.output != "-":
            out_f.close()
