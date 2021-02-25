#!/usr/bin/env python
import sys
import requests
import time
import json
import os
from FinvizTicker import FinvizTicker
from multiprocessing import Pool

# This script runs every day at 5AM to get all contracts in the market

if len(sys.argv) > 1:
    environment = sys.argv[1]

def write_message(message):
    print(message)
    # log to logz API endpoint if in production
    if environment == "PRODUCTION":
        requests.post('http://localhost:5000/Log/Info', json={'message': message})

def slack_message(message):
    requests.post(os.environ['WHEEL_SCREENER_SLACK_WEBHOOK_URL'], json={'text': message})

def call_dotnet_option_calculator_api(tickerName):
    response = requests.post('http://localhost:5000/Wheel/' + tickerName)
    write_message(response.text)
    if response.status_code == 200:
        write_message(tickerName + ' done!')
        return int(response.text), ''
    else:
        write_message(tickerName + ' failed :(')
        return 0, tickerName

def call_dotnet_normalization_endpoint():
    response = requests.post('http://localhost:5000/Wheel/NormalizeDataset')
    if response.status_code == 200:
        data = response.json()
        return data.count
    else:
        return 0

def run_for_tickers(tickers):
    failedTickers = []
    totalStoredCount = 0
    for i in range(0, len(tickers)):
        write_message(str(i+1) + ' of ' + str(len(tickers)) + '...')
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

    # We've tried as much we can, now run the normalization endpoint
    slack_message('Calling normalization endpoint...')
    processed_wheels = call_dotnet_normalization_endpoint()
    slack_message("The normalization endpoint reported processing " + str(processed_wheels) + " wheels!")