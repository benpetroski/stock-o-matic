#!/usr/bin/env python
import time
from FinvizTicker import FinvizTicker
from multiprocessing import Pool
from slack_utils import slack_message

def scrape_ticker(tickername):
    try:
        FinvizTicker(tickername)
    except ConnectionError as e:
        print(e)
    except Exception as e:
        print(e)

count = 0

if __name__ == '__main__':

    slack_message("Starting to get Finviz data for each symbol!")

    # Read in ticker symbol list created by get_finviz_ticker_symbols.py
    with open('data/ticker_symbols_lists/ticker_symbols.dat') as f:
        tickers = f.readlines()

        # Clear ticker symbols of new line character
        for i, ticker in enumerate(tickers):
            print(str(count) + " of " +  str(len(ticker)) + "; ticker: " + ticker)
            tickers[i] = ticker.replace('\n', '')
            count = count + 1

    # Start processes, as they empty, a new case is fed in
    # Processes may need to be tuned to prevent being rate limited by finviz
    pool = Pool(processes=1)
    pool.map(scrape_ticker, tickers)
