from abc import ABC
import sys
from typing import List

import kagglehub
import numpy as np
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


def download_csv(kaggle: str) -> CsvPath:
    """Download a CSV file from Kaggle and return the largest one."""

    cache_dir = kagglehub.dataset_download(
        kaggle,
    )

    files = sorted(CsvPath(cache_dir).glob("*.csv"), key=lambda x: x.size())

    if not files:
        raise FileNotFoundError(f"{kaggle=} has no CSV file(s) in {cache_dir=}")

    file: CsvPath = files[-1]

    # Add some attributes to the file object
    file.kaggle = kaggle

    return file


def earthquake() -> CsvPath:
    """Download the earthquake dataset from Kaggle."""

    return download_csv(
        "alessandrolobello/the-ultimate-earthquake-dataset-from-1990-2023"
    )


def main() -> int:
    try:
        file = earthquake()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        return 1

    lines = file.lines
    size = file.size()

    print(f"{str(size):>10}  {lines:>6}  {file.as_posix()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
