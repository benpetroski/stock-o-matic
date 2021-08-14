#!/usr/bin/env python
import time
from FinvizTicker import FinvizTicker
from multiprocessing import Pool

def scrape_ticker(tickername):
    try:
        FinvizTicker(tickername)
    except ConnectionError as e:
        print("ConnectionError thrown in FinvizTicker:")
        print(e)
        time.sleep(60)
    except Exception as e:
        print("Exception thrown in FinvizTicker:")
        print(e)
    finally:
        print("Continuing...")


if __name__ == '__main__':

    # Read in ticker symbol list created by get_finviz_ticker_symbols.py
    with open('data/ticker_symbols_lists/ticker_symbols.dat') as f:
        tickers = f.readlines()

        # Clear ticker symbols of new line character
        for i, ticker in enumerate(tickers):
            tickers[i] = ticker.replace('\n', '')

    # Start processes, as they empty, a new case is fed in
    # Processes may need to be tuned to prevent being rate limited by finviz
    pool = Pool(processes=1)
    pool.map(scrape_ticker, tickers)
