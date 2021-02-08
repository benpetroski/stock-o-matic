#!/usr/bin/env python

import json
from FinvizTicker import FinvizTicker
from multiprocessing import Pool

def scrapeticker(tickername):
    stock = FinvizTicker(tickername)
    print(tickername)
    return stock.metrics

if __name__ == '__main__':

    # Read in ticker symbol list created by get_finviz_ticker_symbols.py
    with open('ticker_symbols.dat') as f:
        tickers = f.readlines()

        # Clear ticker symbols of new line character
        for i, ticker in enumerate(tickers):
            tickers[i] = ticker.replace('\n', '')

    # Start processes, as they empty, a new case is fed in
    # Processes may need to be tuned to prevent being rate limited by finviz
    pool = Pool(processes=10)
    metrics = pool.map(scrapeticker, tickers)

    # Write the metric data into it's respective ticker file in JSON format
    for i, metric in enumerate(metrics):
        with open('data/tickers/' + tickers[i] + '.json', 'w') as fp:
            json.dump(metric, fp)
