import argparse
import csv
import sys

from csvwrangler.hasher import hash_file


def add_hash_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("hash", help="Hash values in specified columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--columns", required=True, help="Comma-separated list of columns to hash"
    )
    p.add_argument(
        "--algorithm",
        default="sha256",
        choices=["sha256", "sha1", "md5", "sha512"],
        help="Hash algorithm (default: sha256)",
    )
    p.add_argument(
        "--suffix",
        default="_hash",
        help="Suffix for new hash columns (default: _hash)",
    )


def run_hash(args: argparse.Namespace) -> None:
    columns = [c.strip() for c in args.columns.split(",")]
    try:
        with open(args.input, newline="", encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            with open(args.output, "w", newline="", encoding="utf-8") as fout:
                writer = csv.DictWriter(fout, fieldnames=[])
                hash_file(reader, writer, columns, args.algorithm, args.suffix)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
