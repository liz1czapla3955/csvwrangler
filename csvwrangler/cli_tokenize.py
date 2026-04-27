"""CLI sub-command: tokenize"""

import csv
import sys

from csvwrangler.tokenizer import tokenize_rows


def add_tokenize_subparser(subparsers):
    p = subparsers.add_parser(
        "tokenize",
        help="Split a column's values into tokens (split or indicator mode)",
    )
    p.add_argument("input", nargs="?", help="Input CSV file (default: stdin)")
    p.add_argument("-o", "--output", help="Output CSV file (default: stdout)")
    p.add_argument("-c", "--column", required=True, help="Column to tokenize")
    p.add_argument("-s", "--sep", default=" ", help="Token separator (default: space)")
    p.add_argument(
        "-m",
        "--mode",
        choices=["split", "indicator"],
        default="split",
        help="'split' rewrites the column; 'indicator' adds one column per token",
    )
    p.add_argument(
        "--output-sep",
        default="|",
        help="Separator used when joining tokens back (split mode only)",
    )
    p.add_argument(
        "--prefix",
        default="",
        help="Prefix for indicator column names (indicator mode only)",
    )
    p.add_argument(
        "--lowercase",
        action="store_true",
        help="Lowercase all tokens before processing",
    )
    p.set_defaults(func=run_tokenize)
    return p


def run_tokenize(args):
    in_fh = open(args.input, newline="") if args.input else sys.stdin
    out_fh = open(args.output, "w", newline="") if args.output else sys.stdout

    try:
        reader = csv.DictReader(in_fh)
        rows = list(reader)
        if not rows:
            return

        result = list(
            tokenize_rows(
                rows,
                column=args.column,
                sep=args.sep,
                mode=args.mode,
                output_sep=args.output_sep,
                prefix=args.prefix,
                lowercase=args.lowercase,
            )
        )

        fieldnames = list(result[0].keys()) if result else []
        writer = csv.DictWriter(out_fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)
    except (KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        if args.input:
            in_fh.close()
        if args.output:
            out_fh.close()
