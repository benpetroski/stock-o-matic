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
else:
    print("This script requires an environment argument; any one of the following: DEVELOPMENT, STAGING, or PRODUCTION")
    exit()

def getUrl():
    if environment == "PRODUCTION":
        return 'http://localhost:5000'
    if environment == "STAGING":
        return 'http://localhost:4999'
    if environment == "DEVELOP":
        return 'http://localhost:5000'

url = getUrl()
accessId = os.environ['WHEEL_SCREENER_ACCESS_GUID']

def write_message(message, withSlack = False):
    envPrependedMessage = f'{environment}: {message}'
    # always print to stdout
    print(envPrependedMessage)
    # log to logz API endpoint
    requests.post(f'{url}/Log/Info', json={'message': envPrependedMessage})
    if withSlack:
        slack_message(envPrependedMessage)

def slack_message(message):
    requests.post(os.environ['WHEEL_SCREENER_SLACK_WEBHOOK_URL'], json={'text': message})

def call_dotnet_option_calculator_api(tickerName):
    response = requests.post(f'{url}/Wheel/{tickerName}/{accessId}')
    if response.text != '':
        write_message(response.text)
    if response.status_code == 200:
        write_message(tickerName + ' done!')
        return int(response.text), ''
    else:
        write_message(tickerName + ' failed :( Status code: ' + response.status_code)
        return 0, tickerName

def post_dotnet_count_type_endpoint(endpoint):
    response = requests.post(endpoint)
    if response.status_code == 200:
        data = response.json()
        return int(data['count'])
    else:
        return 0

def get_dotnet_count_type_endpoint(endpoint):
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        return int(data['count'])
    else:
        return 0

def get_dotnet_complete_endpoint(endpoint):
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        return data['lastDatasetComplete']
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
    if environment == "PRODUCTION":
        with open('data/ticker_symbols.dat') as f:
            tickers = f.readlines()
    else:
        # dev tickers - shorter list (S&P500) in order to test rapidly
        with open('data/ticker_symbols_s_and_p.dat') as f:
            tickers = f.readlines()

    # Clear ticker symbols of new line character
    for i, ticker in enumerate(tickers):
        tickers[i] = ticker.replace('\n', '')

    # Start processes, as they empty, a new case is fed in
    # Processes need to be throttled to prevent rate limiting by TDAmeritrade
    # pool = Pool(processes=5)
    # pool.map(call_dotnet_option_calculator_api, tickers)

    write_message("Starting the options retrieval process! 🚀", True)
    totalStoredCount, failedTickers = run_for_tickers(tickers)
    write_message('Options retrieval complete!', True)
    write_message('Failed tickers (' + str(len(failedTickers)) + '):', True)
    separator = ', '
    write_message(separator.join(failedTickers), True)
    write_message('Total contracts stored: ' + str(totalStoredCount), True)

    # Try on the failed tickers
    if len(failedTickers) > 0:
        write_message('Retrying failed tickers...', True)
        totalStoredCount, failedTickers =  run_for_tickers(failedTickers)
        write_message('Failed tickers after retry (' + str(len(failedTickers)) + '):', True)
        separator = ', '
        write_message(separator.join(failedTickers), True)
        write_message('Total contracts stored during retry: ' + str(totalStoredCount), True)

    # We've tried as much we can, now run the normalization endpoint
    write_message('Calling normalization endpoint...', True)
    processed_wheels = post_dotnet_count_type_endpoint(f'{url}/Wheel/NormalizeDataset/{accessId}')
    write_message("The normalization endpoint reported processing " + str(processed_wheels) + " wheels!", True)
    
    write_message('Calling random hundred endpoint...', True)
    processed_random_hundred = post_dotnet_count_type_endpoint(f'{url}/Wheel/SetRandomHundred/{accessId}')
    write_message("The random hundred endpoint reported processing " + str(processed_random_hundred) + " wheels!", True)
    
    total_wheels = get_dotnet_count_type_endpoint(f'{url}/Wheel/Count')
    write_message("Cron complete. Total wheels in the database now: " + str(total_wheels), True)
    
    dataset_complete_time = get_dotnet_complete_endpoint(f'{url}/Wheel/LastDatasetComplete')
    write_message("Datetime complete set to: " + str(dataset_complete_time), True)
