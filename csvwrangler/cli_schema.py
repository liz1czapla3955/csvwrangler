"""CLI subcommand for schema inference."""

import argparse
import json
import sys

from csvwrangler.schema_inferrer import format_schema, infer_schema


def add_schema_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'schema' subcommand."""
    parser = subparsers.add_parser(
        'schema',
        help='Infer column types from a CSV file.',
    )
    parser.add_argument('input', help='Path to the input CSV file.')
    parser.add_argument(
        '--delimiter', '-d',
        default=',',
        help='Field delimiter (default: comma).',
    )
    parser.add_argument(
        '--sample-size', '-n',
        type=int,
        default=100,
        dest='sample_size',
        help='Number of rows to sample (default: 100).',
    )
    parser.add_argument(
        '--output-format', '-f',
        choices=['table', 'json'],
        default='table',
        dest='output_format',
        help='Output format: table (default) or json.',
    )
    parser.set_defaults(func=run_schema)


def run_schema(args: argparse.Namespace) -> int:
    """Execute the schema inference command."""
    try:
        schema = infer_schema(
            filepath=args.input,
            sample_size=args.sample_size,
            delimiter=args.delimiter,
        )
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.output_format == 'json':
        print(json.dumps(schema, indent=2))
    else:
        print(format_schema(schema))

    return 0
