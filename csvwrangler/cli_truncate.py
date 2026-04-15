"""CLI subcommand for truncating CSV cell values."""

import argparse
import sys

from csvwrangler.truncator import truncate_file


def add_truncate_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'truncate' subcommand."""
    parser = subparsers.add_parser(
        "truncate",
        help="Truncate cell values to a maximum character length.",
    )
    parser.add_argument("input", help="Path to input CSV file.")
    parser.add_argument("output", help="Path to output CSV file.")
    parser.add_argument(
        "--max-length",
        "-n",
        type=int,
        required=True,
        help="Maximum number of characters per cell value.",
    )
    parser.add_argument(
        "--columns",
        "-c",
        nargs="+",
        default=None,
        metavar="COLUMN",
        help="Columns to truncate. If omitted, all columns are truncated.",
    )
    parser.add_argument(
        "--placeholder",
        default="...",
        help="String appended to truncated values (default: '...').",
    )


def run_truncate(args: argparse.Namespace) -> None:
    """Execute the truncate subcommand."""
    if args.max_length <= 0:
        print(
            f"Error: --max-length must be a positive integer, got {args.max_length}.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        truncate_file(
            input_path=args.input,
            output_path=args.output,
            max_length=args.max_length,
            columns=args.columns,
            placeholder=args.placeholder,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
