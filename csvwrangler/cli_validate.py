"""CLI sub-command: validate — check CSV columns against type/required rules."""

import argparse
import json
import sys

from csvwrangler.validator import validate_file


def add_validate_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "validate",
        help="Validate CSV columns against type and required-field rules.",
    )
    parser.add_argument("input", help="Input CSV file path.")
    parser.add_argument(
        "--type",
        dest="types",
        metavar="COLUMN:TYPE",
        action="append",
        default=[],
        help=(
            "Type rule as COLUMN:TYPE. TYPE must be one of: "
            "integer, float, boolean, date, string. Repeatable."
        ),
    )
    parser.add_argument(
        "--required",
        dest="required",
        metavar="COLUMN",
        action="append",
        default=[],
        help="Mark a column as required (non-empty). Repeatable.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Exit with code 1 if any violations are found.",
    )
    parser.set_defaults(func=run_validate)


def run_validate(args: argparse.Namespace) -> None:
    rules: dict[str, str] = {}
    for item in args.types:
        if ":" not in item:
            print(f"ERROR: --type value must be COLUMN:TYPE, got '{item}'", file=sys.stderr)
            sys.exit(2)
        col, typ = item.split(":", 1)
        rules[col.strip()] = typ.strip()

    try:
        violations = validate_file(args.input, rules, args.required or [])
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    if not violations:
        print("OK: no violations found.")
    else:
        for v in violations:
            print(
                f"Row {v['row']}, column '{v['column']}': {v['reason']}"
            )
        print(f"\n{len(violations)} violation(s) found.")
        if args.fail_fast:
            sys.exit(1)
