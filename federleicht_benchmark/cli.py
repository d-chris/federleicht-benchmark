import sys

import click

from federleicht_benchmark.basic import main as basic_main
from federleicht_benchmark.dataset import main as dataset_main


@click.group()
def cli():
    """CLI to benchmark federleicht."""
    pass


@cli.command(help=dataset_main.__doc__)
@click.option(
    "--cache/--no-cache",
    default=True,
    help="Use cache from kagglehub.",
    show_default=True,
)
def dataset(**kwargs):
    try:
        dataset_main(**kwargs)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


@cli.command(help=basic_main.__doc__)
@click.option(
    "--cache/--no-cache",
    default=True,
    help="Use cache from kagglehub.",
    show_default=True,
)
def basic(**kwargs):
    try:
        basic_main(**kwargs)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)