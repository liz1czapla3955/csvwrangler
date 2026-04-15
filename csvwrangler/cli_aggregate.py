"""CLI sub-command for CSV aggregation."""

import argparse
import sys

from csvwrangler.aggregator import aggregate_file, SUPPORTED_AGGS


def add_aggregate_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'aggregate' sub-command."""
    parser = subparsers.add_parser(
        "aggregate",
        help="Group rows and compute an aggregation (count/sum/min/max/mean).",
    )
    parser.add_argument("input", help="Path to the input CSV file.")
    parser.add_argument("output", help="Path for the output CSV file.")
    parser.add_argument(
        "--group-by",
        required=True,
        metavar="COL",
        nargs="+",
        help="One or more columns to group by.",
    )
    parser.add_argument(
        "--func",
        required=True,
        choices=SUPPORTED_AGGS,
        help="Aggregation function to apply.",
    )
    parser.add_argument(
        "--agg-col",
        metavar="COL",
        default=None,
        help="Column to aggregate (not needed for 'count').",
    )
    parser.set_defaults(handler=run_aggregate)


def run_aggregate(args: argparse.Namespace) -> None:
    """Execute the aggregate sub-command."""
    if args.func != "count" and not args.agg_col:
        print(
            f"Error: --agg-col is required for aggregation function '{args.func}'.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        count = aggregate_file(
            input_path=args.input,
            output_path=args.output,
            group_by=args.group_by,
            agg_column=args.agg_col,
            agg_func=args.func,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Aggregation complete. {count} group(s) written to '{args.output}'.")
