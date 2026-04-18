import argparse
import csv
import sys

from csvwrangler.roller import rolling_file


def add_roll_subparser(subparsers) -> None:
    p = subparsers.add_parser("roll", help="Compute rolling window aggregations")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to aggregate")
    p.add_argument("--window", required=True, type=int, help="Window size")
    p.add_argument(
        "--agg",
        default="mean",
        choices=["mean", "sum", "min", "max"],
        help="Aggregation function (default: mean)",
    )
    p.add_argument("--output-column", default=None, help="Name for result column")


def run_roll(args: argparse.Namespace) -> None:
    if args.window < 1:
        print("Error: --window must be >= 1", file=sys.stderr)
        sys.exit(1)

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            pass
        return

    if args.column not in rows[0]:
        print(f"Error: column '{args.column}' not found", file=sys.stderr)
        sys.exit(1)

    from csvwrangler.roller import rolling_rows
    result = list(rolling_rows(rows, args.column, args.window, args.agg, args.output_column))

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result[0].keys()))
        writer.writeheader()
        writer.writerows(result)
