#!/usr/bin/env python

import urllib2
import re
import time
from HTMLParser import HTMLParser
from math import ceil


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


# Read in ticker symbol list created by get_finviz_ticker_symbols.py
with open('ticker_symbols.dat') as f:
    tickers = f.readlines()

    # Clear ticker symbols of new line character
    for i, ticker in enumerate(tickers):
        tickers[i] = ticker.replace('\n', '')


# Loop through tickers and scrape html
tic = time.clock()
num_tickers = len(tickers)
for i, ticker in enumerate(tickers):
    data = urllib2.urlopen('http://finviz.com/quote.ashx?t=' + ticker).read()
    stripped_data = strip_tags(data)  # strip html tags for raw text

    # Contains all relevant metrics from the table
    metric_strings = ['P/E', 'EPS (ttm)', 'P/C', 'Cash/sh', 'P/C', 'EPS Q/Q', 'LT Debt/Eq', 'Debt/Eq', 'Sales Q/Q',
                      'P/FCF', 'P/C', 'Index', 'Insider Own', 'Shs Outstand', 'Perf Week', 'Perf Year',
                      'Market Cap', 'EPS next Y', 'Insider Trans', 'Shs Float', 'Perf Month', 'Income', 'PEG',
                      'EPS next Q', 'Inst Own', 'Short Float', 'Perf Quarter', 'Sales', 'EPS this Y', 'Inst Trans',
                      'Short Ratio', 'Perf Half Y', 'ROA', 'Target Price', '52W Range', 'Perf YTD', 'Dividend',
                      'EPS past 5Y', 'ROI', '52W High', 'Beta', 'Quick Ratio', 'Sales past 5Y', 'Gross Margin',
                      '52W Low', 'ATR', 'Employees', 'Current Ratio', 'Oper. Margin', 'Volatility', 'Optionable',
                      'Profit Margin', 'Rel Volume', 'Prev Close', 'Shortable', 'Earnings', 'Payout', 'Avg Volume',
                      'Price', 'Recom', 'SMA20', 'SMA50', 'SMA200', 'Volume', 'Change']

    # Loop through metrics, parse, and write dict to file
    data_dict = {}
    for metric_string in metric_strings:
        # search for the name of that metric
        search_string = metric_string.replace('/', '\/').replace('(', '\(').replace(')', '\)') + '(.*)'
        m = re.search(search_string, stripped_data)

        # add the first match of the metric string; also replace metric name with nothing
        data_dict[metric_string] = m.group(0).replace(metric_string, '')

        # write the raw data into its file
        with open('data/' + str(tickers[i]) + '.dat', 'w') as f:
            f.write(str(data_dict))

    time_remaining = ceil((num_tickers - i + 1)*(time.clock() - tic)/(i + 1))
    print 'Completed ' + ticker.ljust(5) + ' (iteration ' + str(i+1).ljust(4) + ' of ' + str(len(tickers)) + ', ' + str(time_remaining) + 's remaining)'
    data_dict.clear()  # flush the entire contents of the dictionary



