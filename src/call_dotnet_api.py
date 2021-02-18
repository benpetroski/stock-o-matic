#!/usr/bin/env python
import requests
import time
import json
from FinvizTicker import FinvizTicker
from multiprocessing import Pool

failedTickers = []

def slack_message(message):
    requests.post('https://hooks.slack.com/services/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', data={'text': message})

# TDAmeritrade is max 120 calls per minute, so we do 1 call ever 0.6 seconds for 100 per minute
def call_dotnet_option_calculator_api(tickerName):
    response = requests.post('http://localhost:5000/Wheel/' + tickerName)
    print(response.text)
    if response.status_code == 200:
        print(tickerName + ' done!')
    else:
        print(tickerName + ' failed :(')
        failedTickers.append(tickerName)

if __name__ == '__main__':

    # Read in ticker symbol list created by get_finviz_ticker_symbols.py
    with open('data/ticker_symbols.dat') as f:
        tickers = f.readlines()

        # Clear ticker symbols of new line character
        for i, ticker in enumerate(tickers):
            tickers[i] = ticker.replace('\n', '')

    # Start processes, as they empty, a new case is fed in
    # Processes need to be throttled to prevent rate limiting by TDAmeritrade
    # pool = Pool(processes=5)
    # pool.map(call_dotnet_option_calculator_api, tickers)
    for i in range(0, len(tickers)):
        print(str(i+1) + ' of ' + str(len(tickers)) + '...')
        with open('data/tickers/' + tickers[i] + '.json') as f:
            metrics = json.load(f)
            if metrics['Optionable']:
                call_dotnet_option_calculator_api(tickers[i])
                time.sleep(0.6)

    slack_message('Options retrieval complete!')
    slack_message('Failed tickers ' + str(len(failedTickers)) + ':')
    slack_message(failedTickers)
