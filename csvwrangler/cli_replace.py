import argparse
import csv
import sys

from csvwrangler.replacer import replace_file


def add_replace_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("replace", help="Replace values in a CSV column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to apply replacement")
    p.add_argument("--pattern", required=True, help="Pattern to search for")
    p.add_argument("--replacement", required=True, help="Replacement string")
    p.add_argument("--regex", action="store_true", help="Treat pattern as regex")
    p.add_argument(
        "--ignore-case", action="store_true", help="Case-insensitive matching"
    )


def run_replace(args: argparse.Namespace) -> None:
    try:
        with open(args.input, newline="") as inf, open(
            args.output, "w", newline=""
        ) as outf:
            reader = csv.DictReader(inf)
            if not reader.fieldnames:
                print("Error: empty input file", file=sys.stderr)
                sys.exit(1)
            writer = csv.DictWriter(outf, fieldnames=reader.fieldnames)
            replace_file(
                reader,
                writer,
                column=args.column,
                pattern=args.pattern,
                replacement=args.replacement,
                use_regex=args.regex,
                case_sensitive=not args.ignore_case,
            )
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
