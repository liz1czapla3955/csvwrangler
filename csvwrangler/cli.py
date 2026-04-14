"""csvwrangler CLI entry point.

Provides command-line interface for CSV transformations,
deduplication, and schema inference.
"""

import argparse
import sys
from csvwrangler import __version__
from csvwrangler.commands import dedupe, infer, transform


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="csvwrangler",
        description="Quick CSV transformations, deduplication, and schema inference.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # --- dedupe subcommand ---
    dedupe_parser = subparsers.add_parser(
        "dedupe",
        help="Remove duplicate rows from a CSV file.",
    )
    dedupe_parser.add_argument("input", help="Path to input CSV file.")
    dedupe_parser.add_argument(
        "-o", "--output", default="-", help="Output file path (default: stdout)."
    )
    dedupe_parser.add_argument(
        "-k", "--keys",
        nargs="+",
        metavar="COLUMN",
        help="Columns to use as deduplication keys (default: all columns).",
    )
    dedupe_parser.add_argument(
        "--delimiter", default=",", help="CSV delimiter (default: ',')."
    )

    # --- infer subcommand ---
    infer_parser = subparsers.add_parser(
        "infer",
        help="Infer schema (column names and types) from a CSV file.",
    )
    infer_parser.add_argument("input", help="Path to input CSV file.")
    infer_parser.add_argument(
        "--delimiter", default=",", help="CSV delimiter (default: ',')."
    )
    infer_parser.add_argument(
        "--sample",
        type=int,
        default=100,
        metavar="N",
        help="Number of rows to sample for inference (default: 100).",
    )
    infer_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )

    # --- transform subcommand ---
    transform_parser = subparsers.add_parser(
        "transform",
        help="Apply transformations to a CSV file.",
    )
    transform_parser.add_argument("input", help="Path to input CSV file.")
    transform_parser.add_argument(
        "-o", "--output", default="-", help="Output file path (default: stdout)."
    )
    transform_parser.add_argument(
        "--delimiter", default=",", help="CSV delimiter (default: ',')."
    )
    transform_parser.add_argument(
        "--select",
        nargs="+",
        metavar="COLUMN",
        help="Select specific columns to include in output.",
    )
    transform_parser.add_argument(
        "--rename",
        nargs="+",
        metavar="OLD=NEW",
        help="Rename columns using OLD=NEW pairs.",
    )
    transform_parser.add_argument(
        "--filter",
        dest="filter_expr",
        metavar="EXPR",
        help="Filter rows by expression, e.g. 'age>30'.",
    )

    return parser


def main() -> None:
    """Main entry point for the csvwrangler CLI."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "dedupe":
            dedupe.run(args)
        elif args.command == "infer":
            infer.run(args)
        elif args.command == "transform":
            transform.run(args)
    except (FileNotFoundError, PermissionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
