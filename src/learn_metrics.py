#!/usr/bin/env python

# Imports
import os.path
from pandas import DataFrame
import numpy as np


# Read in ticker symbol list as created by get_finviz_ticker_symbols.py
with open('finviz_scrape/ticker_symbols.dat') as f:
    tickers = f.readlines()

# Read in metric names
with open('finviz_scrape/metrics.dat') as f:
    metricnames = f.readlines()

# Create metrics dict
metrics = {}
for i in range(len(tickers)):
	fname = 'finviz_scrape/data/data/' + tickers[i].rstrip() + '.dat'
	if(os.path.isfile(fname)):
		metrics[tickers[i].rstrip()] = eval(open(fname, 'r').read())

# Convert dict to DataFrame
tickersFrame = DataFrame(metrics)
tickersFrame[tickersFrame == 'Yes'] = '1' # trust me on the string assignment... makes using rstrip() easier
tickersFrame[tickersFrame == 'No'] = '0'

# Calculate mean metrics
metricSums = []
sumCounts = []
for i in range(len(metricnames)):
	metricSum = 0.0
	sumCount = 0
	for j in range(len(tickers)):
		fname = 'finviz_scrape/data/data/' + tickers[j].rstrip() + '.dat'
		if(os.path.isfile(fname)):
			if tickersFrame[tickers[j].strip()][metricnames[i].strip()] != '-' and metricnames[i].strip() != 'Index': # Skip null values, stock index (NASDAQ, SP500, etc)
				fixedstr = tickersFrame[tickers[j].strip()][metricnames[i].strip()].rstrip('%');
				metricSum = metricSum + float(fixedstr) # given a metric, loop over all stocks, strip % and convert to float!
				sumCount = sumCount + 1
	metricSums.append(metricSum)	
	sumCounts.append(sumCount)		

meanMetrics[:] = np.divide(metricsSum,sumCounts) # Element-wise division: Bad-ass! using pandas and numpy in the same script! (am i real data scientist yet?)

# Print mean metrics to terminal
print 'Mean metrics are:'
for i in range(len(metricnames)):
	print metrics[i] + '  :  ' + meanMetrics[i]

# for i in range(0, numstocks):
# 	for j in range(0,nummetrics):
# 		squareddistance(name_i,i) = squareddistance(name_i, i) + (meanMetrics[j] - metrics(i,j))^2 # We have the name indice in the squareddistance vector just for reference at the end

# Sort stocks by deviation from mean (insightful? Not really at all! but its just a start to get the syntax working with DataFrame)
# sort(squareddistance)
