import json
import os
import requests
from slack_utils import slack_message

if __name__ == '__main__':
    # loop at all tickers in data/ticker_symbols_lists/ticker_symbols/.dat
    # and check if the metric 'Optionable' is true and add to count
    # then print this count to the console
    count = 0
    unknownCount = 0

    # Read in ticker symbol list created by get_finviz_ticker_symbols.py
    with open('data/ticker_symbols_lists/ticker_symbols.dat') as f:
        tickers = f.readlines()

        # Clear ticker symbols of new line character
        for i, ticker in enumerate(tickers):
            # remove the new line character
            ticker = ticker.replace('\n', '')

            # open the json file for the ticker
            with open('data/tickers/' + ticker + '.json') as f:
                metrics = json.load(f)
                try:
                    if metrics['OptionShort']:
                        count += 1
                except KeyError:
                    print("Ticker has no optionable value: " + ticker)
                    unknownCount += 1
                    pass

    print("Optionable Ticker Count: ")
    print(count)
    print("Unknown Ticker Count: ")
    print(unknownCount)
    slack_message("Optionable Ticker Count: " + str(count) + "\nUnknown Ticker Count: " + str(unknownCount))
