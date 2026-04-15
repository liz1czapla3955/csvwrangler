"""CLI sub-command: split."""

import argparse
import sys

from csvwrangler.splitter import split_file


def add_split_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *split* sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "split",
        help="Split a CSV into multiple files based on a column value.",
    )
    parser.add_argument("input", help="Path to the input CSV file.")
    parser.add_argument(
        "--column",
        required=True,
        help="Column whose distinct values determine the output files.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where output files are written (default: current dir).",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="Optional filename prefix for each output file.",
    )
    parser.add_argument(
        "--drop-column",
        action="store_true",
        help="Omit the split column from the output files.",
    )
    parser.set_defaults(func=run_split)


def run_split(args: argparse.Namespace) -> None:
    """Execute the split sub-command."""
    try:
        written = split_file(
            input_path=args.input,
            column=args.column,
            output_dir=args.output_dir,
            prefix=args.prefix,
            keep_column=not args.drop_column,
        )
    except KeyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    for path in written:
        print(path)
