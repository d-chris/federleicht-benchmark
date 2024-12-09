from abc import ABC
from typing import List

import kagglehub
import numpy as np
import pandas as pd
import pathlibutil


class CsvPath(ABC, pathlibutil.Path):
    """
    Inherits from `pathlibutil.Path` and adds some attributes about the dataset from
    Kaggle.
    """

    kaggle: str
    """Kaggle dataset name."""

    @property
    def lines(self) -> int:
        """Count the number of lines in a file."""

        lines = 0
        with self.open("rb") as f:
            while chunk := f.read(200 * 2**20):
                lines += chunk.count(b"\n")

        return lines

    @property
    def chunks(self) -> List[int]:
        """Generate chunks of lines to read from a file."""

        return [
            int(value)
            for value in np.logspace(4, np.log10(self.lines), num=6, dtype=int)
        ]


def download_csv(kaggle: str, **kwargs) -> CsvPath:
    """Download a CSV file from Kaggle and return the largest one."""

    cache_dir = kagglehub.dataset_download(
        kaggle,
        **kwargs,
    )

    files = sorted(CsvPath(cache_dir).glob("*.csv"), key=lambda x: x.size())

    if not files:
        raise FileNotFoundError(f"{kaggle=} has no CSV file(s) in {cache_dir=}")

    file: CsvPath = files[-1]

    # Add some attributes to the file object
    file.kaggle = kaggle

    return file


def earthquake(cache: bool = True) -> CsvPath:
    """Download the earthquake dataset from Kaggle."""

    return download_csv(
        "alessandrolobello/the-ultimate-earthquake-dataset-from-1990-2023",
        force_download=not cache,
    )


def delete_earthquake():
    """Clear the Kaggle cache directory."""

    cache = pathlibutil.Path.home().joinpath(".cache/kagglehub")

    dataset = cache / "datasets/alessandrolobello"

    try:
        dataset.delete(recursive=True)
    except FileNotFoundError:
        pass
    else:
        try:
            cache.rmdir()
        except Exception:
            pass


def main(cache: bool) -> None:
    """Summary of earthquake dataset from kaggle."""

    file = earthquake(cache)

    data = {
        "Size": [str(file.size())],
        "Lines": [file.lines],
        "Filename": [file.as_posix()],
    }

    df = pd.DataFrame(data)

    print("")
    print(df.to_markdown(index=False))
