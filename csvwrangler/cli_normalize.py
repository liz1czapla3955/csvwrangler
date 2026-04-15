"""CLI subcommand: normalize — clean up headers and values in a CSV file."""

from __future__ import annotations

import argparse
import sys

from csvwrangler.renamer import normalize_file


def add_normalize_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "normalize",
        help="Normalize CSV headers and/or values (case, whitespace, char replacement).",
    )
    p.add_argument("input", help="Input CSV file path.")
    p.add_argument("output", help="Output CSV file path.")
    p.add_argument(
        "--header-case",
        choices=["lower", "upper", "title"],
        default=None,
        help="Convert header names to this case.",
    )
    p.add_argument(
        "--value-case",
        choices=["lower", "upper", "title"],
        default=None,
        help="Convert values to this case.",
    )
    p.add_argument(
        "--no-strip",
        action="store_true",
        help="Disable stripping of leading/trailing whitespace.",
    )
    p.add_argument(
        "--replace",
        nargs=2,
        metavar=("OLD", "NEW"),
        action="append",
        default=[],
        help="Replace OLD with NEW in header names (repeatable).",
    )
    p.add_argument(
        "--columns",
        nargs="+",
        default=None,
        help="Limit value normalization to these columns.",
    )


def run_normalize(args: argparse.Namespace) -> None:
    try:
        with open(args.input, newline="", encoding="utf-8") as fh:
            input_text = fh.read()
    except FileNotFoundError:
        print(f"Error: input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    replace_map = {old: new for old, new in args.replace}
    result = normalize_file(
        input_text,
        header_case=args.header_case,
        value_case=args.value_case,
        strip=not args.no_strip,
        replace=replace_map if replace_map else None,
        columns=args.columns,
    )

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        fh.write(result)
    print(f"Normalized CSV written to '{args.output}'.")
