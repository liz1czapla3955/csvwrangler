"""CLI subcommand for masking CSV column values."""
import argparse
import sys

from csvwrangler.masker import mask_file, MASK_MODES


def add_mask_subparser(subparsers) -> None:
    p = subparsers.add_parser("mask", help="Mask or redact values in specified columns.")
    p.add_argument("input", help="Input CSV file (use '-' for stdin).")
    p.add_argument("--columns", required=True, help="Comma-separated list of columns to mask.")
    p.add_argument(
        "--mode",
        choices=MASK_MODES,
        default="full",
        help="Masking mode (default: full).",
    )
    p.add_argument("--char", default="*", help="Replacement character for full/partial modes.")
    p.add_argument("--output", default="-", help="Output file (default: stdout).")
    p.set_defaults(func=run_mask)


def run_mask(args) -> None:
    if args.input == "-":
        text = sys.stdin.read()
    else:
        try:
            with open(args.input, newline="", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

    columns = [c.strip() for c in args.columns.split(",")]

    try:
        result = mask_file(text, columns=columns, mode=args.mode, char=args.char)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output == "-":
        sys.stdout.write(result)
    else:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            f.write(result)
