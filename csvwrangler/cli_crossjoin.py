import argparse
import csv
import sys


def add_crossjoin_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "crossjoin",
        help="Produce the Cartesian product of two CSV files.",
    )
    p.add_argument("left", help="Path to the left CSV file.")
    p.add_argument("right", help="Path to the right CSV file.")
    p.add_argument("-o", "--output", default="-", help="Output file (default: stdout).")
    p.add_argument(
        "--left-prefix",
        default="left_",
        dest="left_prefix",
        help="Prefix for conflicting left columns (default: left_).",
    )
    p.add_argument(
        "--right-prefix",
        default="right_",
        dest="right_prefix",
        help="Prefix for conflicting right columns (default: right_).",
    )
    p.set_defaults(func=run_crossjoin)


def run_crossjoin(args) -> None:
    from csvwrangler.crossjoiner import crossjoin_rows

    try:
        with open(args.left, newline="") as lf, open(args.right, newline="") as rf:
            left_rows = list(csv.DictReader(lf))
            right_rows = list(csv.DictReader(rf))
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    rows = crossjoin_rows(left_rows, right_rows, args.left_prefix, args.right_prefix)

    if args.output == "-":
        out = sys.stdout
    else:
        out = open(args.output, "w", newline="")

    try:
        if rows:
            writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    finally:
        if args.output != "-":
            out.close()
