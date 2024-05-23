#!/usr/bin/env python
import sys
import requests
import time
import json
import os
from slack_utils import slack_message

# This script runs every day at ~5AM to get all contracts in the market
start_at = None

if len(sys.argv) > 1:
    environment = sys.argv[1]
    start_at = sys.argv[2] if len(sys.argv) > 2 else None
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

def call_dotnet_option_calculator_api(tickerName):
    response = requests.post(f'{url}/Wheel/{tickerName}/{accessId}')
    if response.text != '':
        write_message(response.text)
    if response.status_code == 200:
        write_message(tickerName + ' done!')
        return int(response.text), ''
    else:
        write_message(tickerName + ' failed :( Status code: ' + str(response.status_code))
        return 0, tickerName

def call_dotnet_intraday_data_api(tickerName):
    write_message('Calling intraday data endpoint for ' + tickerName)
    response = requests.post(f'{url}/IntradayData/{tickerName}/{accessId}')
    if response.text != '':
        write_message(response.text)
    if response.status_code == 200:
        write_message(tickerName + ' done!')
        return 1, ''
    else:
        write_message(tickerName + ' failed :( Status code: ' + str(response.status_code))
        return 0, tickerName

def call_dotnet_stock_api(tickerName):
    write_message('Calling stock endpoint for ' + tickerName)
    response = requests.post(f'{url}/Stock/{tickerName}/{accessId}')
    if response.text != '':
        write_message(response.text)
    if response.status_code == 200:
        write_message(tickerName + ' done!')
        return 1, ''
    else:
        write_message(tickerName + ' failed :( Status code: ' + str(response.status_code))
        return 0, tickerName

def post_dotnet_count_type_endpoint(endpoint):
    response = requests.post(endpoint)
    if response.status_code == 200:
        data = response.json()
        return int(data['count'])
    else:
        return 0

def post_endpoint(url: str):
    response = requests.post(url)

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
        return data['datasetCompleteDateTime']
    else:
        return 0

def run_for_tickers(tickers):
    failedTickers = []
    totalStoredCount = 0
    for i in range(0, len(tickers)):
        write_message(str(i+1) + ' of ' + str(len(tickers)) + '...')
        # with open('data/tickers/' + tickers[i] + '.json') as f:
        #     metrics = json.load(f)
        #     try:
        #         if metrics['OptionShort']:
                    # first get the actual options for the ticker
        count, tickerName = call_dotnet_option_calculator_api(tickers[i])
        if count > 0:
            # then get the intraday data for the ticker - goes in IntradayData table
            call_dotnet_intraday_data_api(tickers[i])
            # then get the stock data for the ticker - goes in Stock table
            call_dotnet_stock_api(tickers[i])
        totalStoredCount += count
        # if ticker name is not an empty string, there was some sort of error with retrieval
        if tickerName != '':
            failedTickers.append(tickerName)
            # except:
            #     write_message(f'Error retrieving options for {tickers[i]}, skipping...')
    return totalStoredCount, failedTickers

def retrieve_intraday_data(tickers):
    failedTickers = []
    totalStoredCount = 0
    for i in range(0, len(tickers)):
        write_message(str(i+1) + ' of ' + str(len(tickers)) + '...')
        with open('data/tickers/' + tickers[i] + '.json') as f:
            metrics = json.load(f)
            try:
                if metrics['OptionShort']:
                    count, tickerName = call_dotnet_intraday_data_api(tickers[i])
                    call_dotnet_stock_api(tickers[i])
                    totalStoredCount += count
                    # if ticker name is not an empty string, there was some sort of error with retrieval
                    if tickerName != '':
                        failedTickers.append(tickerName)
                        
                    # Alpaca rate limit is max 200 calls per minute, so we do 1 call ever 0.4 seconds for 150 per minute
                    time.sleep(0.4)
            except:
                write_message(f'Error retrieving intraday data for {tickers[i]}, skipping...')
    return totalStoredCount, failedTickers

if __name__ == '__main__':

    if environment != "PRODUCTION" and environment != "STAGING" and environment != "DEVELOP":
        print("Please provide a proper environment - either 'PRODUCTION', 'STAGING', or 'DEVELOP'")
        exit()
    
    # Read in ticker symbol list created by get_finviz_ticker_symbols.py
    if environment == "PRODUCTION":
        with open('data/ticker_symbols_lists/ticker_symbols.dat') as f:
            tickers = f.readlines()
    if environment == "STAGING":
        # staging tickers - shorter list (S&P500) in order to test rapidly
        with open('data/ticker_symbols_lists/ticker_symbols_s_and_p.dat') as f:
            tickers = f.readlines()
    if environment == "DEVELOP":
        # dev tickers - extremely short list of some select tickers (or uncomment the line below to use the S&P500 list)
        with open('data/ticker_symbols_lists/ticker_symbols_development.dat') as f:
        # with open('data/ticker_symbols_lists/ticker_symbols_s_and_p.dat') as f:
            tickers = f.readlines()

    # Clear ticker symbols of new line character
    for i, ticker in enumerate(tickers):
        tickers[i] = ticker.replace('\n', '')

    # If a 'start_at' was passed, we will only run the tickers after that ticker
    if start_at is not None:
        start_index = tickers.index(start_at)
        tickers = tickers[start_index:]

    # Start processes, as they empty, a new case is fed in
    # pool = Pool(processes=5)
    # pool.map(call_dotnet_option_calculator_api, tickers)
    # write_message("Retrieving intraday price data from Alpaca paper trading API...", True)
    # retrieve_intraday_data(tickers)
    # write_message("Alpaca intraday data retrieval complete!", True)

    if start_at is not None:
        write_message("Starting the options retrieval process from ticker " + start_at + "! 🚀", True)
    else:
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
    
    total_wheels = get_dotnet_count_type_endpoint(f'{url}/Wheel/Count')
    write_message("Cron complete. Total strategies in the database now: " + str(total_wheels), True)
    
    dataset_complete_time = get_dotnet_complete_endpoint(f'{url}/DataSetInfo/MostRecent')
    write_message("Datetime complete was set to (via GET at /DataSetInfo/MostRecent): " + str(dataset_complete_time), True)

    # if in staging or production, Post to heartbeat endpoint
    if environment == "STAGING" or environment == "PRODUCTION":
        post_endpoint(os.environ['OPTION_DATASET_HEARTBEAT_ENDPOINT'])
