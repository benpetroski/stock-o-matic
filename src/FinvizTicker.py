#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tzlocal import get_localzone

class FinvizTicker:

    def __init__(self, ticker):
        # Convert the string to uppercase
        self.ticker = ticker.upper()

        # Construct the url from the ticker
        self.url = 'http://finviz.com/quote.ashx?t=' + self.ticker

        # Download the ticker, and parse using beautiful soup
        html = requests.get(self.url)
        self._data = BeautifulSoup(html.content, features="html.parser")
        self.time_stamp = datetime.now(get_localzone())

        # Check if the page exists - note b for bytes like object
        if b'We cover only stocks and ETFs listed on NYSE, NASDAQ, and AMEX. International and OTC/PK are not available.' in html.content:
            raise ImportError('Stock ticker \'' + self.ticker + '\' does not exist in the Finviz database.')

        # Parse the html and create the metrics dictionary
        self.metrics = self._get_metrics()


    def _get_metrics(self):
        # Extract the main table with ticker data and create a list of the rows in the table
        table = self._data.find('table', {'class': 'snapshot-table2'})
        rows = table.findAll('tr')

        # Loop through the rows and build a dictionary of the elements
        metrics = {}
        for tr in rows:

            # Extracts the columns of each row
            cols = tr.findAll('td')

            # Check if there is an even number of columns (should always be)
            if len(cols) % 2 == 0:

                # Extract out the unicode and convert to a raw string
                data = [ col.text for col in cols ]
                keys = [ str(key) for key in data[0::2] ]
                values = [ str(value) for value in data[1::2] ]

                # Add the row in to the metric database
                metrics.update(zip(keys, values))
            else:
                raise ImportError('Dude, the finviz table doesn''t have an even number of columns!')

        return metrics
    
    # metrics getter
    def getMetrics(self):
        return self.metrics

    def __str__(self):
        return '%s: $%s\nretrieved on %s' % (self.ticker, self.metrics['Price'], self.time_stamp.strftime('%Y-%m-%d %H:%M:%S %Z'))