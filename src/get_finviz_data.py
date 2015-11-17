#!/usr/bin/env python

import threading
import urllib2
import re
import time
from HTMLParser import HTMLParser
from math import ceil
from FinvizTicker import FinvizTicker
import sys
from multiprocessing import Pool

def scrapeticker(tickername):
    stock = FinvizTicker(tickername)
    print tickername
    return stock.metrics

# Read in ticker symbol list created by get_finviz_ticker_symbols.py
with open('ticker_symbols.dat') as f:
    tickers = f.readlines()

    # Clear ticker symbols of new line character
    for i, ticker in enumerate(tickers):
        tickers[i] = ticker.replace('\n', '')

# Start 100 processes, as they empty, a new case is fed in
tic = time.clock()
pool = Pool(processes=100)
metrics = pool.map(scrapeticker, tickers)

# Write the raw data into its file
for i, metric in enumerate(metrics):
    with open('data/' + tickers[i] + '.dat', 'w') as fout:
        fout.write(str(metric))
    fout.close()
