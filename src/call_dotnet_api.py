#!/usr/bin/env python
import requests
import time
import json
import os
from FinvizTicker import FinvizTicker
from multiprocessing import Pool

def slack_message(message):
    requests.post(os.environ['WHEEL_SCREENER_SLACK_WEBHOOK_URL'], json={'text': message})

def call_dotnet_option_calculator_api(tickerName):
    response = requests.post('http://localhost:5000/Wheel/' + tickerName)
    print(response.text)
    if response.status_code == 200:
        print(tickerName + ' done!')
        return int(response.text), ''
    else:
        print(tickerName + ' failed :(')
        return -1, tickerName

def call_dotnet_completion_endpoint():
    response = requests.post('http://localhost:5000/CompleteDataset')
    return response.status_code == 200

def run_for_tickers(tickers):
    failedTickers = []
    totalStoredCount = 0
    for i in range(0, len(tickers)):
        print(str(i+1) + ' of ' + str(len(tickers)) + '...')
        with open('data/tickers/' + tickers[i] + '.json') as f:
            metrics = json.load(f)
            if metrics['Optionable']:
                count, tickerName = call_dotnet_option_calculator_api(tickers[i])
                totalStoredCount += count
                # if ticker name is not an emptry string, there was some sort of error with retrieval
                if tickerName != '':
                    failedTickers.append(tickerName)
                # TDAmeritrade is max 120 calls per minute, so we do 1 call ever 0.6 seconds for 100 per minute
                time.sleep(0.6)
    return totalStoredCount, failedTickers

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

        slack_message("Starting today's scrape! 🚀")
        totalStoredCount, failedTickers = run_for_tickers(tickers)
        slack_message('Options retrieval complete!')
        slack_message('Failed tickers (' + str(len(failedTickers)) + '):')
        separator = ', '
        slack_message(separator.join(failedTickers))
        slack_message('Total contracts stored: ' + str(totalStoredCount))

        # Try on the failed tickers
        slack_message('Retrying failed tickers...')
        totalStoredCount, failedTickers =  run_for_tickers(failedTickers)
        slack_message('Failed tickers after retry (' + str(len(failedTickers)) + '):')
        separator = ', '
        slack_message(separator.join(failedTickers))
        slack_message('Total contracts stored during retry: ' + str(totalStoredCount))

        slack_message('Calling completion endpoint...')
        success = call_dotnet_completion_endpoint()
        if success:
            slack_message("Success! Today's dataset is ready to rip!")
        else:
            slack_message("Uh oh! Looks like something went wrong with the completion endpoint!")



    

