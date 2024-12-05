import timeit
from datetime import datetime, timedelta
from typing import Callable, Union

import pandas as pd
from federleicht import clear_cache
from federleicht.config import CACHE
from pathlibutil import Path
from tqdm import tqdm

from federleicht_benchmark.dataset import CsvPath, earthquake
from federleicht_benchmark.feder import read_csv, read_data


def backup_cache() -> None:
    """Backup the caches."""
    cache_dir = Path(CACHE.dir)

    if not cache_dir.exists():
        return

    for file in cache_dir.iterdir():
        if file.is_file() and file.suffix != ".bak":
            try:
                file.rename(file.with_suffix(".bak"))
            except FileExistsError:
                file.unlink()


def restore_cache() -> None:
    """Restore the default cache names."""
    cache_dir = Path(CACHE.dir)

    if not cache_dir.exists():
        return

    for file in cache_dir.glob("*.bak"):
        try:
            file.rename(file.with_suffix(""))
        except FileExistsError:
            file.unlink()


def benchmark(
    func: Callable,
    *,
    file: CsvPath,
    repeat: int = 3,
    verbose: bool = True,
    setup: Union[Callable, str] = "pass",
    **kwargs,
) -> pd.DataFrame:
    """
    Run the benchmark for the given function and return the results as a DataFrame.
    """
    data = dict()

    # Check if the function is wrapped and get the original function name
    name = kwargs.get("name", func.__name__)
    total_lines = sum(file.chunks) * repeat

    proccessed_lines = 0
    total_seconds = 0
    start = datetime.now()

    with tqdm(
        total=len(file.chunks),
        desc=name,
        disable=not verbose,
        bar_format="{desc:<12}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}{postfix}",
    ) as pbar:
        for nrows in file.chunks:
            time = timeit.repeat(
                lambda: func(file, nrows=nrows),
                setup=setup,
                repeat=repeat,
                number=1,
            )

            rows_per_iteration = nrows * repeat
            proccessed_lines += rows_per_iteration

            seconds_per_iteration = sum(time)
            total_seconds += seconds_per_iteration

            seconds_per_row = seconds_per_iteration / rows_per_iteration

            finished_in_seconds = (total_lines - proccessed_lines) * seconds_per_row

            eta = datetime.now() + timedelta(seconds=finished_in_seconds)

            pbar.set_postfix()

            pbar.set_postfix_str(f"  eta: {eta:%H:%M:%S}")
            pbar.update(1)

            data[nrows] = time

        total = datetime.now() - start

        pbar.set_postfix_str(f"total:  {str(total).split('.')[0]}")
        pbar.refresh()

    df = pd.DataFrame.from_dict(data, orient="index")

    df.attrs.update(
        {
            "file": file.as_posix(),
            # "func": name,
            "repeat": repeat,
            "lines": file.lines,
            "kaggle": file.kaggle,
            "setup": setup.__name__ if callable(setup) else setup,
            "total": total.total_seconds(),
        }
    )

    return df


def main(
    cache: bool,
    runs: int,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Compare direct read, cache build, and cache read times using timeit for different
    numbers of rows.
    """

    file = earthquake(cache)

    print("")

    kwargs = {
        "file": file,
        "repeat": runs,
        "verbose": verbose,
    }

    df = dict()

    key = "read_data"
    df[key] = benchmark(
        read_csv,
        name=key,
        **kwargs,
    )

    clear_cache()

    key = "build_cache"
    df[key] = benchmark(
        read_data,
        setup=backup_cache,
        name=key,
        **kwargs,
    )

    restore_cache()

    key = "read_cache"
    df[key] = benchmark(
        read_data,
        name=key,
        **kwargs,
    )

    clear_cache()

    df = pd.DataFrame({key: frame.mean(axis=1) for key, frame in df.items()})

    df.index.name = "nrows"

    if verbose:
        print("")
        print(df.to_markdown(floatfmt=".3f"))

    return df


if __name__ == "__main__":
    main(False, 1)
