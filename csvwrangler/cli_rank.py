import argparse
import csv
import sys

from csvwrangler.ranker import rank_file


def add_rank_subparser(subparsers) -> None:
    p = subparsers.add_parser("rank", help="Add a rank column based on a numeric or string column.")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to rank by")
    p.add_argument("--rank-column", default="rank", help="Name of the new rank column (default: rank)")
    p.add_argument(
        "--method",
        choices=["dense", "standard", "row"],
        default="dense",
        help="Ranking method (default: dense)",
    )
    p.add_argument("--desc", action="store_true", help="Rank in descending order")


def run_rank(args) -> None:
    try:
        with open(args.input, newline="", encoding="utf-8") as inf:
            reader = csv.DictReader(inf)
            rows = list(reader)
            if not rows:
                print("Input file is empty.", file=sys.stderr)
                sys.exit(1)
            fieldnames = list(rows[0].keys()) + [args.rank_column]
            with open(args.output, "w", newline="", encoding="utf-8") as outf:
                writer = csv.DictWriter(outf, fieldnames=fieldnames)
                import io
                from csvwrangler.ranker import rank_rows
                ranked = rank_rows(
                    rows,
                    column=args.column,
                    rank_column=args.rank_column,
                    method=args.method,
                    ascending=not args.desc,
                )
                writer.writeheader()
                for row in ranked:
                    writer.writerow(row)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
