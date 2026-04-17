import sys
import csv
from csvwrangler.deduplicator import deduplicate_file


def add_dedup_subparser(subparsers):
    p = subparsers.add_parser("dedup", help="Remove duplicate rows from a CSV file")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="COLUMN",
        help="Columns to use as dedup key (default: all columns)",
    )
    p.add_argument(
        "--keep",
        choices=["first", "last"],
        default="first",
        help="Which duplicate to keep (default: first)",
    )
    p.set_defaults(func=run_dedup)


def run_dedup(args):
    try:
        with open(args.input, newline="", encoding="utf-8") as inf, \
             open(args.output, "w", newline="", encoding="utf-8") as outf:
            reader = csv.DictReader(inf)
            if reader.fieldnames is None:
                print("Error: empty or invalid CSV", file=sys.stderr)
                sys.exit(1)
            fieldnames = list(reader.fieldnames)
            keys = args.keys or None
            if keys:
                missing = [k for k in keys if k not in fieldnames]
                if missing:
                    print(f"Error: key columns not found: {missing}", file=sys.stderr)
                    sys.exit(1)
            rows = list(reader)
            deduped = deduplicate_file(rows, key_fields=keys, keep=args.keep)
            writer = csv.DictWriter(outf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(deduped)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
