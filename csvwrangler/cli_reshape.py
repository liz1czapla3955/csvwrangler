"""CLI subcommand for reshaping CSV files (melt / unmelt)."""

from __future__ import annotations

import argparse
import sys

from csvwrangler.reshaper import reshape_file


def add_reshape_subparser(subparsers) -> None:
    """Register the 'reshape' subcommand."""
    parser = subparsers.add_parser(
        "reshape",
        help="Reshape CSV between wide and long formats.",
    )
    parser.add_argument("input", help="Input CSV file path.")
    parser.add_argument("output", help="Output CSV file path.")
    parser.add_argument(
        "--mode",
        choices=["melt", "unmelt"],
        required=True,
        help="'melt' converts wide→long; 'unmelt' converts long→wide.",
    )
    parser.add_argument(
        "--id-vars",
        required=True,
        nargs="+",
        metavar="COL",
        help="Columns to use as identifier variables.",
    )
    parser.add_argument(
        "--value-vars",
        nargs="+",
        metavar="COL",
        help="(melt) Columns to unpivot.",
    )
    parser.add_argument(
        "--var-name",
        default="variable",
        help="(melt) Name for the new variable column. Default: 'variable'.",
    )
    parser.add_argument(
        "--value-name",
        default="value",
        help="(melt) Name for the new value column. Default: 'value'.",
    )
    parser.add_argument(
        "--var-col",
        default="variable",
        help="(unmelt) Column containing variable names. Default: 'variable'.",
    )
    parser.add_argument(
        "--value-col",
        default="value",
        help="(unmelt) Column containing values. Default: 'value'.",
    )
    parser.set_defaults(func=run_reshape)


def run_reshape(args: argparse.Namespace) -> None:
    """Execute the reshape subcommand."""
    try:
        reshape_file(
            input_path=args.input,
            output_path=args.output,
            mode=args.mode,
            id_vars=args.id_vars,
            value_vars=args.value_vars,
            var_name=args.var_name,
            value_name=args.value_name,
            var_col=args.var_col,
            value_col=args.value_col,
        )
        print(f"Reshaped '{args.input}' → '{args.output}' (mode={args.mode}).")
    except (KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
