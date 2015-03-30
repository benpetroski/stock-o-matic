#!/usr/bin/env python

import urllib2
import itertools
import xml.etree
from HTMLParser import HTMLParser
import re

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

with open('stock_tickers.txt') as f:
	tickers = f.readlines()

#possibletickers = [];
validtickers = [];
validcount = 0;
# for p in itertools.permutations('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 1): # 1 letter stock tickers
# 	possibletickers.append(''.join(p));
# for p in itertools.permutations('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 2): # 2 letter stock tickers
# 	possibletickers.append(''.join(p));
# for p in itertools.permutations('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 3): # 3 letter stock tickers
# 	possibletickers.append(''.join(p));
# for p in itertools.permutations('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 4): # 4 letter stock tickers
# 	possibletickers.append(''.join(p));

#print possibletickers

for i in range(0,len(tickers)):
	print 'On iteration ' + str(i) + ' of ' + str(len(tickers)) + ' tickers...'
	
	try:
		usock = urllib2.urlopen('http://finviz.com/quote.ashx?t=' + tickers[i])
	except urllib2.HTTPError:
		print 'Stock ticker ' + tickers[i] + ' not found on finviz.com or returned 404! Moving on...'
		continue
		
	else: # SCRAPE! GET ON YOUR HORSE!!!!!
		validtickers.append(tickers[i])
		
		scrapedata = usock.read()


		strippedscrape = strip_tags(scrapedata) # strip html tags for raw text
		
		# Metrics we have to manually pull because their regex's need escaping (I know, not the most efficient but it works)
		m = re.search('P\/E(.*)', strippedscrape)
		PE = m.group(0).replace('P/E', '')
		datadict = {'P/E' : PE}

		m = re.search('EPS \(ttm\)(.*)', strippedscrape)
		EPS = m.group(0).replace('EPS (ttm)', '')
		datadict['EPS (ttm)'] = EPS

		m = re.search('Cash\/sh(.*)', strippedscrape)
		CashSh = m.group(0).replace('Cash/sh', '')
		datadict['Cash/sh'] = CashSh

		m = re.search('P\/C(.*)', strippedscrape)
		PC = m.group(0).replace('P/C', '')
		datadict['P/C'] = PC

		m = re.search('P\/FCF(.*)', strippedscrape)
		PFCF = m.group(0).replace('P/FCF', '')
		datadict['P/FCF'] = PFCF

		m = re.search('Sales Q\/Q(.*)', strippedscrape)
		SalesQQ = m.group(0).replace('Sales Q/Q', '')
		datadict['Sales Q/Q1'] = SalesQQ

		m = re.search('RSI \(14\)(.*)', strippedscrape)
		RSI14 = m.group(0).replace('RSI (14)', '')
		datadict['RSI (14)'] = RSI14

		m = re.search('Debt\/Eq(.*)', strippedscrape)
		DebtEq = m.group(0).replace('Debt/Eq', '')
		datadict['Debt/Eq'] = DebtEq

		m = re.search('EPS Q\/Q(.*)', strippedscrape)
		EPSQQ = m.group(0).replace('EPS Q/Q', '')
		datadict['EPS Q/Q'] = EPSQQ

		m = re.search('LT Debt/Eq(.*)', strippedscrape)
		LTDebtEq = m.group(0).replace('LT Debt/Eq', '')
		datadict['LT Debt/Eq'] = LTDebtEq

		# For the metrics that don't need special escape characters in the actual regex, we can loop with pattern
		metricstrings = ['Index', 'Insider Own', 'Shs Outstand', 'Perf Week', 'Perf Year', 'Market Cap', 'EPS next Y', 'Insider Trans', \
		'Shs Float', 'Perf Month', 'Income', 'PEG', 'EPS next Q', 'Inst Own', 'Short Float', 'Perf Quarter', 'Sales', 'EPS this Y', \
		'Inst Trans', 'Short Ratio', 'Perf Half Y', 'ROA', 'Target Price', '52W Range', 'Perf YTD', 'Dividend', 'EPS past 5Y', \
		'ROI', '52W High', 'Beta', 'Quick Ratio', 'Sales past 5Y', 'Gross Margin', '52W Low', 'ATR', 'Employees', 'Current Ratio', \
		'Oper. Margin', 'Volatility', 'Optionable', 'Profit Margin', 'Rel Volume', 'Prev Close', 'Shortable', 'Earnings', \
		'Payout', 'Avg Volume', 'Price', 'Recom', 'SMA20', 'SMA50', 'SMA200', 'Volume', 'Change']

		for j in range(0, len(metricstrings)):
			m = re.search(metricstrings[j] + '(.*)', strippedscrape) # search for the name of that metric
			#print m.group(0)
			datadict[metricstrings[j]] = m.group(0).replace(metricstrings[j], '') # add the group 0 (first match) of that metric, but also replace the metric name itself with nothing (delete it!)

		#print datadict

		tickers[i].strip() # remove whitespace
		with open('finvizdata2/' + str(tickers[i]) + '.txt', 'w') as f:
  			f.write(str(datadict)) # write the raw

  		datadict.clear() # flush the entire contents of the dictionary

