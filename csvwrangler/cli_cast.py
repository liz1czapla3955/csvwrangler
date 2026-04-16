"""CLI subcommand for casting CSV column types."""
import sys
import csv
import io
from csvwrangler.caster import cast_file, SUPPORTED_TYPES


def add_cast_subparser(subparsers):
    p = subparsers.add_parser("cast", help="Cast column values to a specified type")
    p.add_argument("input", help="Input CSV file (use '-' for stdin)")
    p.add_argument("output", help="Output CSV file (use '-' for stdout)")
    p.add_argument(
        "--col",
        dest="casts",
        metavar="COLUMN:TYPE",
        action="append",
        required=True,
        help=(
            f"Column and target type, e.g. age:int. "
            f"Supported types: {', '.join(sorted(SUPPORTED_TYPES))}. "
            "Repeat for multiple columns."
        ),
    )
    p.add_argument(
        "--errors",
        choices=["raise", "ignore"],
        default="raise",
        help="How to handle cast errors (default: raise)",
    )
    return p


def run_cast(args):
    casts = {}
    for item in args.casts:
        if ":" not in item:
            print(f"Error: --col value must be COLUMN:TYPE, got {item!r}", file=sys.stderr)
            sys.exit(1)
        col, dtype = item.split(":", 1)
        if dtype not in SUPPORTED_TYPES:
            print(f"Error: unsupported type {dtype!r}. Choose from {SUPPORTED_TYPES}", file=sys.stderr)
            sys.exit(1)
        casts[col] = dtype

    if args.input == "-":
        input_text = sys.stdin.read()
    else:
        with open(args.input, newline="", encoding="utf-8") as f:
            input_text = f.read()

    try:
        result = cast_file(input_text, casts, errors=args.errors)
    except (ValueError, TypeError) as e:
        print(f"Cast error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output == "-":
        sys.stdout.write(result)
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            f.write(result)
