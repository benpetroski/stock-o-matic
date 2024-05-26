#!/usr/bin/python

import os
import time
import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from pytz import timezone
from supabase import create_client

eastern = timezone('US/Eastern')

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
indexes = ['DJIA', 'S&P500', 'AMEX', 'NASDAQ', 'NYSE', 'S&P']
lastUpdatedFormat = '%Y-%m-%d'
# lastUpdatedFormat = '%Y-%m-%d %H:%M:%S %Z'
lastUpdatedKeyName = 'LastUpdated'

def load_env_file(file_path):
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        except FileNotFoundError:
            print(f"Error: The file {file_path} was not found.")
        except Exception as e:
            print(f"Error: {e}")

class FinvizTicker:
    def __init__(self, ticker):
        # load env
        load_env_file('.env')

        # get supabase url and key from environment
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        # if either not set, warn and return error
        if not supabase_url or not supabase_key:
            print('Error: SUPABASE_URL or SUPABASE_KEY not set in environment, cannot upload to supabase.')
        else:
            # set supabase client on this
            self.supabase = create_client(supabase_url, supabase_key)

        # Convert the string to uppercase
        self.ticker = ticker.upper()

        # Current timestamp
        self.time_stamp = datetime.now(eastern).strftime(lastUpdatedFormat)

        # First check if the file exists
        try:
            with open('data/tickers/' + self.ticker + '.json', 'r') as json_file:
                pass
        except FileNotFoundError:
            print("Ticker file doesn't exist, creating it...")
            with open('data/tickers/' + self.ticker + '.json', 'w') as json_file:
                json.dump({}, json_file)

        # First check if we've already written this in the past day
        with open('data/tickers/' + self.ticker + '.json', 'r') as json_file:
            data = json.load(json_file)
            try:
                lastUpdated = data[lastUpdatedKeyName]
                if lastUpdated == self.time_stamp:
                    print("We've already got this ticker's data (" + self.ticker + ") for the day! We'll try again tomorrow :)")
                    return
            except:
                print("No 'lastUpdated' key found, gonna go ahead and scrape this ticker! (", self.ticker, ")")

        # Construct the url from the ticker
        self.url = 'http://finviz.com/quote.ashx?t=' + self.ticker

        # Download the ticker, and parse using beautiful soup
        # time.sleep(1)
        # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"}
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 9_9_3; en-US) Gecko/20130401 Firefox/72.9"}
        response = requests.get(self.url, headers=headers)
        self._data = BeautifulSoup(response.content, 'html.parser')
        # this is poor, if the scrape includes these words by coincidence, we'll get a false positive
        # better would be to use request library to check the status code
        if  len(self._data.text) < 5000 and ('Access denied' in self._data.text or 'Error' in self._data.text):
            print('Woops, Finviz is rate limiting us right now! Gonna sleep for one minute...')
            time.sleep(60)
            raise ConnectionError('rate limited by Finviz')

        # Check if the page exists - note b for bytes like object
        if b'We cover only stocks and ETFs listed on NYSE, NASDAQ, and AMEX. International and OTC/PK are not available.' in response.content:
            raise ImportError('Stock ticker \'' + self.ticker + '\' does not exist on the Finviz website.')

        # Parse the html and create the metrics dictionary
        print("Getting metrics for ticker: " + self.ticker)
        self.metrics = self._get_metrics()

        # Write metrics to json and upload to supabase
        self.write_metrics()
        self.upload_metrics_to_supabase()

    def _convert_to_float(self, value):
        try:
            return float(value)
        except ValueError:
            return ''

    def _get_metrics(self):
        # init vars
        metrics = {}
        keys = []
        values = []

        # Get the sector, industry, and location
        keys.extend(['Sector', 'Industry', 'Country', 'Exchange'])
        values.extend(['','','', ''])

        quoteLinks = self._data.find('div', {'class': 'quote-links'})
        if quoteLinks is not None:
            tabLinks = quoteLinks.findAll('a', {'class': 'tab-link'})
            for i in range(0,4):
                if tabLinks[i] is None:
                    continue
                text = tabLinks[i].text.strip()
                values[i] = text

        # Extract the main table with ticker data and create a list of the rows in the table
        table = self._data.find('table', {'class': 'snapshot-table2'})
        if table is None:
            raise ValueError("Table is NoneType dude! BeautifulSoup object: " + self._data.text)
        rows = table.findAll('tr')

        # Loop through the rows and build a dictionary of the elements
        for tr in rows:
            # Extracts the columns of each row
            cols = tr.findAll('td')

            if cols is None:
                raise ValueError("Columns weren't found in the table dude!")

            # Check if there is an even number of columns (should always be)
            if len(cols) % 2 == 0:
                
                # Extract out the unicode and convert to a raw string
                data = [ col.text for col in cols ]

                # for each key, clean up name so it is JSON compatible
                for key in data[0::2]:
                    key = str(key)
                    key = key.replace('%', 'Percent')
                    key = key.replace('/', '')
                    key = key.replace('(', '')
                    key = key.replace(')', '')
                    key = key.replace('.', '')
                    key = key.replace('52', 'FiftyTwo')
                    key = key.replace(' ', '')
                    keys.append(key)

                # for each value, clean up value 
                for value in data[1::2]:
                    value = str(value)
                    # empty values - en dash
                    if value == '-':
                        values.append('')
                        continue
                    
                    # empty values — em dash
                    if value == '—':
                        values.append('')
                        continue

                    # for the rare triple dash!
                    if value == '- - -':
                        values.append('')
                        continue
                    # append index just as string
                    found = False
                    for index in indexes:
                        if index in value:
                            found = True
                    
                    if found:
                        values.append(value)
                        continue

                    # remove percents and commas
                    value = value.replace('%', '')
                    value = value.replace(',', '')

                    # remove front and back parentheses
                    value = value.replace('(', '')
                    value = value.replace(')', '')

                    # TODO: fix this so we can also add shortable somehow
                    # Option/Short 'Yes / Yes'
                    if value == "Yes / Yes" or value == "Yes / No":
                        values.append(True)
                        continue
                    # Option/Short 'Yes / No'
                    if value == "No / Yes" or value == "No / No":
                        values.append(False)
                        continue
                    # earnings string has month and day, just append this value as string
                    if value[0:3] in months:
                        values.append(value)
                        continue
                    # category also has a dash, but could have the following
                    if 'US Equities -' in value:
                        values.append(value)
                        continue
                    if 'Bonds -' in value:
                        values.append(value)
                        continue
                    if 'Global or ExUS Equities -' in value:
                        values.append(value)
                        continue
                    
                    if 'Commodities & Metals -' in value:
                        values.append(value)
                        continue

                    if 'Target Date / Multi-Asset' in value:
                        values.append(value)
                        continue

                    if 'Equity -' in value:
                        values.append(value)
                        continue

                    if 'Equities -' in value:
                        values.append(value)
                        continue

                    # 52 week range has this dash, split to array and convert to float
                    if ' - ' in value:
                        rangeValues = value.split(' - ')
                        # can't do much here, just leave empty value
                        if rangeValues[0] == '-':
                            values.append('')
                            continue
                        # sometimes it only has one vol value, can only append the first
                        if rangeValues[1] == '-':
                            values.append([self._convert_to_float(rangeValues[0])])
                            continue
                        # otherwise append the array of both
                        values.append([self._convert_to_float(rangeValues[0]), self._convert_to_float(rangeValues[1])])
                        continue
                    # volatility has two values, split to array and convert to float
                    if value.count(' ') == 1:
                        volatilityVals = value.split(' ')
                        # can't do much here, just leave empty value
                        if volatilityVals[0] == '-':
                            values.append('')
                            continue
                        # sometimes it only has one vol value, can only append the first
                        if volatilityVals[1] == '-':
                            values.append([self._convert_to_float(volatilityVals[0])])
                            continue
                        # otherwise append the array of both
                        values.append([self._convert_to_float(volatilityVals[0]), self._convert_to_float(volatilityVals[1])])
                        continue
                    # convert to thousands
                    if value[-1] == 'K':
                        value = value.replace('K', '')
                        value = self._convert_to_float(value)*1000
                        values.append(value)
                        continue
                    # convert to millions
                    if value[-1] == 'M':
                        value = value.replace('M', '')
                        value = self._convert_to_float(value)*1000000
                        values.append(value)
                        continue
                    # convert to billions
                    if value[-1] == 'B':
                        value = value.replace('B', '')
                        value = self._convert_to_float(value)*1000000000
                        values.append(value)
                        continue
                    # default
                    values.append(value)

                # Custom metric: last updated so we can skip this ticker if the whole process crashes
                keys.append(lastUpdatedKeyName)
                values.append(self.time_stamp)

                # Add the key value pair to the metric list
                metrics.update(zip(keys, values))
            else:
                raise ImportError("Dude, the finviz table doesn't have an even number of columns!")

        print("Got " + str(len(values)) + " metrics for ticker: " + self.ticker + " - Optionable? " + str(metrics['OptionShort']))
        return metrics
    
    def write_metrics(self):
        with open('data/tickers/' + self.ticker + '.json', 'w') as fp:
            json.dump(self.metrics, fp)
    
    def upload_metrics_to_supabase(self):
        metrics_json = json.dumps(self.metrics)
        data = self.supabase.table('finviz').upsert({
            'ticker': self.ticker,
            'data': metrics_json
        }).execute()
        if len(data.data) > 0:
            print(f"Successfully uploaded {self.ticker} to supabase")
        else:
            print(f"Error uploading {self.ticker} to supabase")

    # string representation
    def __str__(self):
        return '%s: $%s\nretrieved on %s' % (self.ticker, self.metrics['Price'], self.time_stamp)