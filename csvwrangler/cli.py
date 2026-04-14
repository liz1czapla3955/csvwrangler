"""Entry point for the csvwrangler CLI."""

import argparse
import sys

from csvwrangler.cli_dedup import add_dedup_subparser
from csvwrangler.cli_schema import add_schema_subparser
from csvwrangler.cli_sort import add_sort_subparser
from csvwrangler.cli_transform import add_transform_subparser  # noqa: F401 – kept for future use


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="csvwrangler",
        description=(
            "Quick CSV transformations, deduplication, schema inference, "
            "and sorting — no pandas required."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="<command>",
    )
    subparsers.required = True

    add_dedup_subparser(subparsers)
    add_schema_subparser(subparsers)
    add_sort_subparser(subparsers)

    return parser


def main(argv=None) -> None:
    """Parse arguments and dispatch to the appropriate sub-command handler."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if hasattr(args, "func"):
        args.func(args)
    else:  # pragma: no cover
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
