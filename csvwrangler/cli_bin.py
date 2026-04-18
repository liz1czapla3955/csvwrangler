import argparse
import csv
import sys

from csvwrangler.binner import bin_file


def add_bin_subparser(subparsers) -> None:
    p = subparsers.add_parser("bin", help="Assign rows to numeric bins")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to bin")
    p.add_argument(
        "--edges",
        required=True,
        help="Comma-separated bin edges, e.g. 0,10,20,30",
    )
    p.add_argument(
        "--labels",
        default=None,
        help="Comma-separated labels (must be len(edges)+1)",
    )
    p.add_argument(
        "--output-column",
        default="bin",
        dest="output_column",
        help="Name of the output bin column (default: bin)",
    )


def run_bin(args: argparse.Namespace) -> None:
    try:
        edges = [float(e) for e in args.edges.split(",")]
    except ValueError:
        print("Error: --edges must be comma-separated numbers", file=sys.stderr)
        sys.exit(1)

    labels = None
    if args.labels:
        labels = [l.strip() for l in args.labels.split(",")]

    try:
        with open(args.input, newline="") as inf, open(
            args.output, "w", newline=""
        ) as outf:
            reader = csv.DictReader(inf)
            if not reader.fieldnames:
                return
            out_fields = list(reader.fieldnames) + (
                [args.output_column]
                if args.output_column not in reader.fieldnames
                else []
            )
            writer = csv.DictWriter(outf, fieldnames=out_fields)
            bin_file(reader, writer, args.column, edges, labels, args.output_column)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
