import argparse
import sys
from csvwrangler.transformer import transform_file


def add_transform_subparser(subparsers):
    p = subparsers.add_parser(
        "transform",
        help="Filter rows, select/rename columns, or add computed columns",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument(
        "--filter",
        metavar="COL=VALUE",
        dest="filter_expr",
        help="Keep rows where COL equals VALUE",
    )
    p.add_argument(
        "--negate",
        action="store_true",
        help="Negate the filter condition",
    )
    p.add_argument(
        "--select",
        metavar="COL",
        nargs="+",
        help="Select only these columns (in order)",
    )
    p.add_argument(
        "--rename",
        metavar="OLD=NEW",
        nargs="+",
        help="Rename columns using OLD=NEW pairs",
    )
    p.add_argument(
        "--add-column",
        metavar="NAME=VALUE",
        dest="add_column",
        help="Add a new column with a constant value",
    )
    p.set_defaults(func=run_transform)
    return p


def run_transform(args):
    filter_col, filter_val = None, None
    if args.filter_expr:
        if "=" not in args.filter_expr:
            print(f"Error: --filter must be COL=VALUE, got {args.filter_expr!r}", file=sys.stderr)
            sys.exit(1)
        filter_col, filter_val = args.filter_expr.split("=", 1)

    rename_map = {}
    if args.rename:
        for pair in args.rename:
            if "=" not in pair:
                print(f"Error: --rename must be OLD=NEW, got {pair!r}", file=sys.stderr)
                sys.exit(1)
            old, new = pair.split("=", 1)
            rename_map[old] = new

    add_col_name, add_col_value = None, None
    if args.add_column:
        if "=" not in args.add_column:
            print(f"Error: --add-column must be NAME=VALUE, got {args.add_column!r}", file=sys.stderr)
            sys.exit(1)
        add_col_name, add_col_value = args.add_column.split("=", 1)

    transform_file(
        args.input,
        args.output,
        filter_col=filter_col,
        filter_val=filter_val,
        negate=args.negate,
        select=args.select,
        rename=rename_map if rename_map else None,
        add_col_name=add_col_name,
        add_col_value=add_col_value,
    )
