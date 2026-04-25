"""CLI sub-command: extract — filter rows by regex pattern."""
import csv
import sys

from csvwrangler.extractor import extract_rows


def add_extract_subparser(subparsers) -> None:
    p = subparsers.add_parser(
        "extract",
        help="Keep (or remove) rows whose columns match a regex pattern.",
    )
    p.add_argument("input", nargs="?", default="-", help="Input CSV file (default: stdin)")
    p.add_argument("-o", "--output", default="-", help="Output CSV file (default: stdout)")
    p.add_argument(
        "-c", "--columns", required=True,
        help="Comma-separated column names to search.",
    )
    p.add_argument("-p", "--pattern", required=True, help="Regular-expression pattern.")
    p.add_argument(
        "-v", "--invert", action="store_true",
        help="Invert match — keep rows that do NOT match.",
    )
    p.add_argument(
        "--capture-column",
        default=None,
        metavar="NAME",
        help="Add a column with the first captured group (or full match).",
    )
    p.set_defaults(func=run_extract)


def run_extract(args) -> None:
    columns = [c.strip() for c in args.columns.split(",")]

    in_fh = open(args.input, newline="", encoding="utf-8") if args.input != "-" else sys.stdin
    out_fh = open(args.output, "w", newline="", encoding="utf-8") if args.output != "-" else sys.stdout

    try:
        reader = csv.DictReader(in_fh)
        fieldnames_known = False
        writer = None

        for row in extract_rows(
            reader,
            columns,
            args.pattern,
            invert=args.invert,
            output_column=args.capture_column,
        ):
            if not fieldnames_known:
                writer = csv.DictWriter(out_fh, fieldnames=list(row.keys()))
                writer.writeheader()
                fieldnames_known = True
            writer.writerow(row)
    finally:
        if args.input != "-":
            in_fh.close()
        if args.output != "-":
            out_fh.close()
