To run the benchmarks, do the following (assuming cwd at top level):

    $ pip install -r tests/benchmarks/requirements.txt

Then, run the benchmarks as a script:

    $ ./tests/benchmarks/benchmarks.py

You can also run them using pytest:

    $ pytest --benchmark-warmup=on tests/benchmarks/benchmarks.py
