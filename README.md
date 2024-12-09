# federleicht-benchmark

small project to test the performance of the pypi package.

![PyPI - Version](https://img.shields.io/pypi/v/federleicht?logo=pypi&logoColor=orange&label=federleicht)

## usage

```cmd
# federleicht --help

Usage: federleicht [OPTIONS] COMMAND [ARGS]...

  CLI to benchmark federleicht.

Options:
  --help  Show this message and exit.

Commands:
  basic      Basic benchmark to test cache build and access time.
  benchmark  Compare direct read, cache build, and cache read times using...
  dataset    Summary of earthquake dataset from kaggle.
```

## basic

download dataset from kaggle and call the decorated function twice to see the difference in execution time.

![basic](basic.gif)

## benchamrk

use timeit to compare the execution time of direct read, cache build, and cache read for different number of lines in the dataset.

![benchmark](benchmark.gif)
