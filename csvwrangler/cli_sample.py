"""CLI subcommand for CSV row sampling."""

import argparse
import sys

from csvwrangler.sampler import sample_file


def add_sample_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'sample' subcommand."""
    parser = subparsers.add_parser(
        "sample",
        help="Sample rows from a CSV file.",
    )
    parser.add_argument("input", help="Input CSV file path.")
    parser.add_argument("output", help="Output CSV file path.")
    parser.add_argument(
        "-n",
        "--num-rows",
        type=int,
        required=True,
        dest="num_rows",
        help="Number of rows to sample.",
    )
    parser.add_argument(
        "--mode",
        choices=["random", "first", "last"],
        default="random",
        help="Sampling strategy (default: random).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (random mode only).",
    )
    parser.set_defaults(func=run_sample)


def run_sample(args: argparse.Namespace) -> None:
    """Execute the sample subcommand."""
    try:
        count = sample_file(
            input_path=args.input,
            output_path=args.output,
            n=args.num_rows,
            mode=args.mode,
            seed=args.seed,
        )
        print(f"Wrote {count} sampled row(s) to {args.output}")
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
