import argparse
import csv
import sys

from csvwrangler.outlier import outlier_file


def add_outlier_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("outlier", help="Detect or mark outliers in a numeric column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to analyse")
    p.add_argument("--threshold", type=float, default=3.0, help="Z-score threshold (default: 3.0)")
    p.add_argument(
        "--mark",
        action="store_true",
        help="Mark rows instead of filtering; adds a boolean column",
    )
    p.add_argument(
        "--mark-column",
        default="is_outlier",
        dest="mark_column",
        help="Name of the marker column (default: is_outlier)",
    )


def run_outlier(args: argparse.Namespace) -> None:
    try:
        with open(args.input, newline="", encoding="utf-8") as fin:
            reader = csv.DictReader(fin)
            if reader.fieldnames is None:
                print("Error: empty input file", file=sys.stderr)
                sys.exit(1)
            if args.column not in reader.fieldnames:
                print(f"Error: column '{args.column}' not found", file=sys.stderr)
                sys.exit(1)
            with open(args.output, "w", newline="", encoding="utf-8") as fout:
                writer = csv.DictWriter(fout, fieldnames=[])
                outlier_file(
                    reader,
                    writer,
                    column=args.column,
                    threshold=args.threshold,
                    mark=args.mark,
                    mark_column=args.mark_column,
                )
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
