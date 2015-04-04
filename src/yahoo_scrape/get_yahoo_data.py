import urllib
import time
import pandas as pd
from xml.dom.minidom import parseString


def generate_url(symbols):
    # Generates the query url used from the query yahoo API (YQL). Uses standard SQL in the q parameter. Appears to be
    # no limit on query length. Have tested up to 500 tickers in a single request.

    query_string = 'select * from yahoo.finance.quotes where symbol in ('
    for j, symbol in enumerate(symbols):
        if j != 0:
            query_string += ',"' + symbol + '"'
        else:
            query_string += '"' + symbol + '"'
    query_string += ')'

    # Construct the url with a url encoded version of the query string
    url = 'https://query.yahooapis.com/v1/public/yql?'
    params = {'env': 'store://datatables.org/alltableswithkeys', 'diagnostics': 'true', 'q': query_string}
    return url + urllib.urlencode(params)


# Read in the S&P500 csv file and create a list of all tickers in the S&P500
df = pd.read_csv('SP500.csv')
tickers = df.Symbol.values.tolist()

# Record the time and download the xml file containing the results
time_string = time.strftime("%Y%m%d-%H%M%S")
f = urllib.urlopen(generate_url(tickers))
data = f.read()
f.close()

# Begin parsing the xml
dom = parseString(data)
stocks = dom.getElementsByTagName('quote')
for i, stock in enumerate(stocks):

    # Store data both in subset xml files as well as a dict string for easy importing
    filename_xml = 'data/' + tickers[i] + '_' + time_string + '.xml'
    filename_dict = 'data/' + tickers[i] + '_' + time_string + '.dict'

    # Dive into the xml structure.
    children = stock.childNodes
    dict_array = {}
    for child in children:
        key = child.nodeName  # attribute (Ask, Bid, DaysLow, etc)

        # Check if there is a value. Most stocks have empty nodes
        if len(child.childNodes) > 0:
            value = child.childNodes[0].nodeValue  # attribute value
        else:
            value = None

        dict_array[key] = value

    # Save the original xml decomposed into stock specific xml files
    with open(filename_xml, "w") as text_file:
        text_file.write(stock.toprettyxml())

    # Save the parsed dictionary
    with open(filename_dict, "w") as text_file:
        text_file.write(str(dict_array))

    # Wipe the dictionary just in case for the next loop iteration
    dict_array.clear()