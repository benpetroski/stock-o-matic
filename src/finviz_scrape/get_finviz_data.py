#!/usr/bin/env python

import threading
import urllib2
import re
import time
from HTMLParser import HTMLParser
from math import ceil
import sys


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

def scrapeticker(tickername, url):
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.HTTPError:
        print "Ticker " + tickername + " could not be found because\ndevon hasn't gotten his act together to fix his ticker script! Moving to next ticker...\n"
        return 
    stripped_data = strip_tags(data)  # strip html tags for raw text

    # Contains all relevant metrics from the table

    # metricNames = ['P/E', 'EPS (ttm)', 'P/C', 'Cash/sh', 'P/C', 'EPS Q/Q', 'LT Debt/Eq', 'Debt/Eq', 'Sales Q/Q',
    #                   'P/FCF', 'P/C', 'Index', 'Insider Own', 'Shs Outstand', 'Perf Week', 'Perf Year',
    #                   'Market Cap', 'EPS next Y', 'Insider Trans', 'Shs Float', 'Perf Month', 'Income', 'PEG',
    #                   'EPS next Q', 'Inst Own', 'Short Float', 'Perf Quarter', 'Sales', 'EPS this Y', 'Inst Trans',
    #                   'Short Ratio', 'Perf Half Y', 'ROA', 'Target Price', '52W Range', 'Perf YTD', 'Dividend',
    #                   'EPS past 5Y', 'ROI', '52W High', 'Beta', 'Quick Ratio', 'Sales past 5Y', 'Gross Margin',
    #                   '52W Low', 'ATR', 'Employees', 'Current Ratio', 'Oper. Margin', 'Volatility', 'Optionable',
    #                   'Profit Margin', 'Rel Volume', 'Prev Close', 'Shortable', 'Earnings', 'Payout', 'Avg Volume',
    #                   'Price', 'Recom', 'SMA20', 'SMA50', 'SMA200', 'Volume', 'Change']

    # Loop through metrics, parse, and write dict to file
    data_dict = {}
    for metricName in metricNames:
        # search for the name of that metric
        metricName = metricName.strip() # remove the newline since it was read in from a file
        if metricName == 'Sales Q/Q1': 
            metricName = 'Sales Q/Q' # i don't know why but for some reason we cant keep the "1" in this metric
        search_string = metricName.replace('/', '\/').replace('(', '\(').replace(')', '\)') + '(.*)'
        m = re.search(search_string, stripped_data)

        # add the first match of the metric string; also replace metric name with nothing
        data_dict[metricName] = m.group(0).replace(metricName, '')

    # cant believe we didn't include the stockname itself in the stock's dictionary!!!
    data_dict['stockname'] = tickername

    if 'Oper. Margin' in data_dict.keys(): # fix for the "." in the "Oper. Margin" key name - can't have that if we use mongoDB - should fix in writing script!!!!
        data_dict['Oper Margin'] = data_dict.pop('Oper. Margin')

    # write the raw data into its file
    with open('data/' + tickername + '.dat', 'w') as f:
        #print "writing" + tickername + " url is: " + url
        f.write(str(data_dict))
    f.close()

    data_dict.clear()  # flush the entire contents of the dictionary


# Read in ticker symbol list created by get_finviz_ticker_symbols.py
with open('ticker_symbols.dat') as f:
    tickers = f.readlines()

    # Clear ticker symbols of new line character
    for i, ticker in enumerate(tickers):
        tickers[i] = ticker.replace('\n', '')


# global stuff we only have to do once
# Read in metric names
with open('metrics.dat') as f:
    metricNames = f.readlines()        

# Loop through tickers and scrape html
batchsize = 1000 # i'm not sure how much we can max this out - a number on the web said "start at 100 and go from there"
tic = time.clock()
for i in range(0,len(tickers),batchsize):

    # prepare this batch of thread variables
    tickerstrs = []
    urls = []

    if abs(len(tickers) - i+batchsize) < batchsize or i+batchsize > len(tickers): # this means we are on the last stocks... (the "remainder" if you will that won't fit in the batch number pattern) need to go from i to the len(tickers)
        start = i
        end = len(tickers)
        for k in range(start,end):
            tickerstrs.append(tickers[k])
            urls.append('http://finviz.com/quote.ashx?t=' + tickers[k])

        # designate thread targets    
        specialrange = end-start
        threads = [threading.Thread(target=scrapeticker, args=(tickerstrs[j], urls[j])) for j in range(specialrange)]

    else:
        start = i
        end = i+batchsize
        for k in range(start,end):
            tickerstrs.append(tickers[k])
            urls.append('http://finviz.com/quote.ashx?t=' + tickers[k])

        # designate thread targets    
        threads = [threading.Thread(target=scrapeticker, args=(tickerstrs[j], urls[j])) for j in range(batchsize)]

    # start and join threads!
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    time_remaining = ceil((len(tickers) - i + 1)*(time.clock() - tic)/(i + 1))
    print 'Completed tickers ' + tickers[start] + ' through ' + tickers[end-1] + ' (stocks ' + str(start) + ' through ' + str(end) + ' of ' + str(len(tickers)) + ', ' + str(time_remaining) + 's remaining)'

