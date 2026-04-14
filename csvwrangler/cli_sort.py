"""CLI sub-command for sorting CSV files."""

import argparse
import sys

from csvwrangler.sorter import sort_file


def add_sort_subparser(subparsers) -> None:
    """Register the 'sort' sub-command on *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "sort",
        help="Sort CSV rows by one or more columns.",
    )
    parser.add_argument("input", help="Path to the input CSV file.")
    parser.add_argument("output", help="Path for the sorted output CSV file.")
    parser.add_argument(
        "-k",
        "--keys",
        required=True,
        nargs="+",
        metavar="COLUMN",
        help="One or more column names to sort by (left = highest priority).",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        default=False,
        help="Sort in descending order.",
    )
    parser.add_argument(
        "-n",
        "--numeric",
        action="store_true",
        default=False,
        help="Treat sort key values as numbers.",
    )
    parser.add_argument(
        "-d",
        "--delimiter",
        default=",",
        help="Field delimiter (default: comma).",
    )
    parser.set_defaults(func=run_sort)


def run_sort(args: argparse.Namespace) -> None:
    """Execute the sort sub-command."""
    try:
        count = sort_file(
            input_path=args.input,
            output_path=args.output,
            keys=args.keys,
            reverse=args.reverse,
            numeric=args.numeric,
            delimiter=args.delimiter,
        )
        print(f"Sorted {count} row(s) → {args.output}")
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        sys.exit(1)
