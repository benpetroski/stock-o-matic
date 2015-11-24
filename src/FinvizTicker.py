import requests
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np
import base64


class FinvizTicker:

    def __init__(self, symbol):
        # Convert the string to uppercase
        self.symbol = symbol.upper()

        # Construct the url from the ticker
        self.url = 'http://finviz.com/quote.ashx?t=' + self.symbol

        # Download the ticker, and parse using beautiful soup
        html = requests.get(self.url)
        self._data = BeautifulSoup(html.content)
        self.time_stamp = datetime.now(tzlocal())

        # Check if the page exists
        if 'We cover only stocks and ETFs listed on NYSE, NASDAQ, and AMEX. International and OTC/PK are not available.' in html.content:
            raise ImportError('Stock symbol \'' + self.symbol + '\' does not exist in the Finviz database.')

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
                data = [col.text for col in cols]
                keys = [clean_varname(key) for key in data[0::2]]
                values = [clean_value(value) for value in data[1::2]]

                # Add the row in to the metric database
                metrics.update(zip(keys, values))
            else:
                raise ImportError('Dude, the finviz table doesn''t have an even number of columns!')

        return metrics

    def __str__(self):
        return '%s: $%s\nretrieved on %s' % (self.symbol, self.metrics['Price'], ticker.time_stamp.strftime('%Y-%m-%d %H:%M:%S %Z'))


def clean_value(value):

    # First convert it to a string
    value = str(value)

    try:
        return float(value)
    except ValueError:
        pass

    # Check if it is a number with a string
    if value[-1:] == 'B':
        return float(value[0:-1])*1e9
    elif value[-1:] == 'M':
        return float(value[0:-1])*1e6

    # Now check if it is a percentage
    if value[-1:] == '%':
        return float(value[0:-1])/100

    # Check for boolean responses
    if value == 'Yes':
        return True
    if value == 'No':
        return False

    # Check for blank entries
    if value == '-':
        return np.nan

    return value

print clean_value('BBdf')

def clean_varname(varname):

    varname = str(varname)
    varname.replace('.', '\p')
    varname.replace('$', '\d')
    return varname


def revert_varname(varname):

    varname.replace('\p', '.')
    varname.replace('\d', '$')

    return varname