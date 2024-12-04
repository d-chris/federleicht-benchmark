"""
poetry install
poetry shell
asciinema rec basic.cast --cols 120 --rows 18
federmark basic
agg basic.cast basic.gif --theme github-dark --speed 2.5 --font-size 20 \
    --last-frame-duration 7
"""

from time import perf_counter as pc

import pandas as pd
from federleicht import clear_cache
from yaspin import yaspin
from yaspin.spinners import Spinners

from federleicht_benchmark.dataset import CsvPath, earthquake
from federleicht_benchmark.feder import read_data


def main(cache: bool) -> None:
    """
    Basic benchmark to test cache build and access time.
    """

    filename: CsvPath = earthquake(cache)
    print("")

    with yaspin(Spinners.line, text="read cache", color="green") as sp:

        clear_cache()
        sp.write("> cache cleared")

        start = pc()
        _ = read_data(filename)
        build = pc() - start
        sp.write("> cache built")

        start = pc()
        df = read_data(filename)
        read = pc() - start
        sp.ok("!")

    file = {
        "filename": filename.name,
        "size": filename.size().string(),
        "lines": filename.lines,
        "seconds": build,
    }

    cachename = CsvPath(df.attrs["from_cache"])

    cache = {
        "filename": cachename.name,
        "size": cachename.size().string(),
        "lines": df.shape[0],
        "seconds": read,
    }

    df = pd.DataFrame(
        {
            "build_cache": file,
            "read_cache": cache,
        }
    )

    print("")
    print(df.to_markdown())
