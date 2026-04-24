"""CLI sub-command: lag / lead column values."""

import csv
import sys

from csvwrangler.lagged import lag_file


def add_lag_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "lag",
        help="Add a column with lagged or lead values from another column.",
    )
    p.add_argument("input", nargs="?", help="Input CSV file (default: stdin)")
    p.add_argument("-o", "--output", help="Output CSV file (default: stdout)")
    p.add_argument("-c", "--column", required=True, help="Source column name")
    p.add_argument(
        "-n",
        "--periods",
        type=int,
        default=1,
        dest="n",
        help="Number of periods to shift (default: 1)",
    )
    p.add_argument(
        "--output-column",
        default=None,
        help="Name for the new column (default: auto-generated)",
    )
    p.add_argument(
        "--fill",
        default="",
        help="Fill value for missing positions (default: empty string)",
    )
    p.add_argument(
        "--lead",
        action="store_true",
        help="Shift forward (lead) instead of backward (lag)",
    )
    p.set_defaults(func=run_lag)


def run_lag(args) -> None:
    in_fh = open(args.input, newline="") if args.input else sys.stdin
    out_fh = open(args.output, "w", newline="") if args.output else sys.stdout

    try:
        reader = csv.DictReader(in_fh)
        # fieldnames will be set inside lag_file once we know the output cols
        writer = csv.DictWriter(out_fh, fieldnames=[])

        if args.column not in (reader.fieldnames or []):
            print(
                f"error: column '{args.column}' not found in input",
                file=sys.stderr,
            )
            sys.exit(1)

        lag_file(
            reader,
            writer,
            column=args.column,
            n=args.n,
            output_column=args.output_column,
            fill=args.fill,
            lead=args.lead,
        )
    finally:
        if args.input:
            in_fh.close()
        if args.output:
            out_fh.close()
