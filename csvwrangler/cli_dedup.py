"""CLI helpers for the dedup subcommand."""

import sys
from argparse import ArgumentParser, Namespace

from csvwrangler.deduplicator import deduplicate_file


def add_dedup_subparser(subparsers) -> None:
    """Register the 'dedup' subcommand on the provided subparsers object."""
    parser: ArgumentParser = subparsers.add_parser(
        "dedup",
        help="Remove duplicate rows from a CSV file.",
    )
    parser.add_argument("input", help="Path to the input CSV file.")
    parser.add_argument("output", help="Path to write the deduplicated CSV file.")
    parser.add_argument(
        "--key-fields",
        dest="key_fields",
        metavar="FIELD",
        nargs="+",
        default=None,
        help="Field names to use as the uniqueness key. Defaults to all fields.",
    )
    parser.add_argument(
        "--keep",
        choices=["first", "last"],
        default="first",
        help="Which duplicate occurrence to keep (default: first).",
    )
    parser.set_defaults(func=run_dedup)


def run_dedup(args: Namespace) -> int:
    """Execute the dedup subcommand.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    try:
        original, deduped = deduplicate_file(
            input_path=args.input,
            output_path=args.output,
            key_fields=args.key_fields,
            keep=args.keep,
        )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    removed = original - deduped
    print(
        f"Deduplicated '{args.input}' → '{args.output}': "
        f"{original} rows in, {deduped} rows out, {removed} duplicates removed."
    )
    return 0
