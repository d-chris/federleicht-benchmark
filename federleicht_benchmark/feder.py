import pandas as pd
from federleicht import cache_dataframe


def read_csv(file: str, nrows: int = None, **kwargs) -> pd.DataFrame:
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


read_data = cache_dataframe(read_csv)
"""Decorated function to cache the DataFrame returned by `read_csv`."""
