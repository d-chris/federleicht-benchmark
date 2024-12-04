import os
import sys
from time import perf_counter as pc

import pandas as pd
from federleicht import cache_dataframe, clear_cache
from yaspin import yaspin
from yaspin.spinners import Spinners

from federleicht_benchmark.dataset import CsvPath, earthquake


@cache_dataframe
def read_data(file: str, nrows: int = None, **kwargs) -> pd.DataFrame:
    """
    Read n rows of the dataset from a CSV file.

    Perform some data type conversions and return the DataFrame.
    """
    df = pd.read_csv(
        file,
        header=0,
        nrows=nrows,
        dtype={
            "status": "category",
            "tsunami": "boolean",
            "data_type": "category",
            "state": "category",
        },
        **kwargs,
    )

    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df["date"] = pd.to_datetime(df["date"], format="mixed")

    return df


def main():

    filename: CsvPath = earthquake()
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


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
