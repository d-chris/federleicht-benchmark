import sys

import click

from federleicht_benchmark.basic import main as basic_main
from federleicht_benchmark.benchmark import main as benchmark_main
from federleicht_benchmark.dataset import delete_earthquake
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
@click.option(
    "--clear",
    is_flag=True,
    help="Clear the cache directory.",
)
def dataset(**kwargs):
    try:
        if kwargs.pop("clear", False):
            delete_earthquake()
        else:
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


@cli.command(help=benchmark_main.__doc__)
@click.option(
    "--cache/--no-cache",
    default=True,
    help="Use cache from kagglehub.",
    show_default=True,
)
@click.option(
    "--runs",
    default=1,
    metavar="N",
    help="Number of repetitions.",
    show_default=True,
)
def benchmark(**kwargs):
    try:
        benchmark_main(**kwargs)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
