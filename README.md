# stock-o-matic

## Virtual Environment

There is a venv within the src directory. Before running scripts, make sure you activate the venv:

```bash
source venv/bin/activate
```

You can double check that all requirements are installed with:

```bash
pip3 install -r requirements.txt
```

The data from finviz should be periodically updated in order to reflect active tickers (for example, FB changed to META, and many more happen on a monthly / weekly basis). The ticker database for each company can be updated by running:

```bash
cd src
python3 get_finviz_ticker_symbols.py
```

As of early 2023, the total number of tickers finviz tracks is 8,364. This script takes about 2 minutes to run.

As of late 2023, the total number of tickers finviz tracks is 8,682.

Then, separate .json files (one per ticker with all metrics) can be created for each ticker by running:

```bash
cd src
python3 get_finviz_data.py
```

This script has to visit any new tickers and any old tickers that need updates, and can take up to 2-3 hours to run.

Then, to get the count of optionable tickers, run:

```bash
cd src
python3 get_optionable_symbol_count.py
```

Run the .NET option downloader for development environment:

```bash
cd src
python3 run_wheel_retrieval_process.py DEVELOP
```

For the staging environment:

```bash
cd src
python3 run_wheel_retrieval_process.py STAGING
```

and for a production environment:

```bash
cd src
python3 run_wheel_retrieval_process.py PRODUCTION
```