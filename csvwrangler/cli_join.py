"""CLI subcommand for joining two CSV files."""

import argparse
import sys

from csvwrangler.joiner import join_files


def add_join_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'join' subcommand."""
    parser = subparsers.add_parser(
        "join",
        help="Join two CSV files on a common key column.",
    )
    parser.add_argument("left", help="Path to the left CSV file.")
    parser.add_argument("right", help="Path to the right CSV file.")
    parser.add_argument("-k", "--key", required=True, help="Column name to join on.")
    parser.add_argument(
        "--how",
        choices=["inner", "left", "right"],
        default="inner",
        help="Join type (default: inner).",
    )
    parser.add_argument("-o", "--output", default="-", help="Output file path (default: stdout).")


def run_join(args: argparse.Namespace) -> None:
    """Execute the join subcommand."""
    try:
        with open(args.left, newline="") as left_fh, open(args.right, newline="") as right_fh:
            if args.output == "-":
                count = join_files(left_fh, right_fh, sys.stdout, key=args.key, how=args.how)
            else:
                with open(args.output, "w", newline="") as out_fh:
                    count = join_files(left_fh, right_fh, out_fh, key=args.key, how=args.how)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Joined {count} row(s).", file=sys.stderr)
