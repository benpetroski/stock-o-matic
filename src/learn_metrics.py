#!/usr/bin/env python

# Imports
import os.path
from pandas import DataFrame
import numpy as np
import operator
import matplotlib.pyplot as plt

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

# Read in ticker symbol list as created by get_finviz_ticker_symbols.py
with open('finviz_scrape/ticker_symbols.dat') as f:
    tickers = f.readlines()

# Read in metric names
with open('finviz_scrape/metrics.dat') as f:
    metricNames = f.readlines()

# Create metrics python dict
metrics = {}
for i in range(len(tickers)):
	fname = 'finviz_scrape/data/data/' + tickers[i].rstrip() + '.dat'
	if(os.path.isfile(fname)):
		metrics[tickers[i].rstrip()] = eval(open(fname, 'r').read())

# Convert dict to DataFrame (I love DataFrames)
tickersFrame = DataFrame(metrics)

# Some cleaning
tickersFrame[tickersFrame == 'Yes'] = '1' # trust me on the string assignment... makes using rstrip() easier later
tickersFrame[tickersFrame == 'No'] = '0'

# Calculation of mean metrics
metricSums = []
sumCounts = []
for i in range(len(metricNames)):
	metricSum = 0.0
	sumCount = 0
	for j in range(len(tickers)):
		fname = 'finviz_scrape/data/data/' + tickers[j].rstrip() + '.dat'
		if(os.path.isfile(fname)):
			# Skip null values, stock indexs (NASDAQ, SP500, etc) (basically this if statement is to filter out any non-number metrics or wacky ones i didn't feel like fixing)
			if tickersFrame[tickers[j].strip()][metricNames[i].strip()] != '-' \
				and metricNames[i].strip() != 'Index' \
				and metricNames[i].strip() != 'Income' \
				and metricNames[i].strip() != 'PEG' \
				and metricNames[i].strip() != '52W Range' \
				and metricNames[i].strip() != 'Earnings' \
				and metricNames[i].strip() != 'Volatility': 
				fixedstr = tickersFrame[tickers[j].strip()][metricNames[i].strip()]
				fixedstr = fixedstr.rstrip('%');
				fixedstr = fixedstr.rstrip('D')
				fixedstr = fixedstr.rstrip('M')
				fixedstr = fixedstr.rstrip('K')
				fixedstr = fixedstr.rstrip('B')
				if hasNumbers(fixedstr):
					metricSum = metricSum + float(fixedstr) # given a metric, loop over all stocks, strip % and convert to float!
					sumCount = sumCount + 1
	metricSums.append(metricSum)	
	sumCounts.append(sumCount)		

meanMetrics = []
meanMetrics = np.divide(metricSums,sumCounts) # Element-wise division: Bad-ass! using pandas and numpy in the same script! (am i real data scientist yet?)
meanMetrics = meanMetrics.tolist()
# Print mean metrics to terminal
print 'Mean metrics are:'
for i in range(len(metricNames)):
	print metricNames[i].strip() + '  :  ' + str(meanMetrics[i])

# Now a very simple calculation of squared distance to the mean
squaredDistance = {}
for i in range(len(tickers)):
	squaredDistanceSum = 0
	for j in range(len(metricNames)):
		fname = 'finviz_scrape/data/data/' + tickers[i].rstrip() + '.dat'
		if(os.path.isfile(fname)):
			# Skip null values, stock indexs (NASDAQ, SP500, etc) (basically this if statement is to filter out any non-number metrics or wacky ones i didn't feel like fixing)
			if tickersFrame[tickers[i].strip()][metricNames[j].strip()] != '-' \
				and metricNames[j].strip() != 'Index' \
				and metricNames[j].strip() != 'Income' \
				and metricNames[j].strip() != 'PEG' \
				and metricNames[j].strip() != '52W Range' \
				and metricNames[j].strip() != 'Earnings' \
				and metricNames[j].strip() != 'Volatility': 
				fixedstr = tickersFrame[tickers[i].strip()][metricNames[j].strip()]
				fixedstr = fixedstr.rstrip('%');
				fixedstr = fixedstr.rstrip('D')
				fixedstr = fixedstr.rstrip('M')
				fixedstr = fixedstr.rstrip('K')
				fixedstr = fixedstr.rstrip('B')
				if hasNumbers(fixedstr):
					squaredDistanceSum = squaredDistanceSum + (meanMetrics[j] - float(fixedstr))**2 # We have the name indice in the squareddistance vector just for reference at the end

	squaredDistance[tickers[i].strip()] = squaredDistanceSum # create dictionary of stockname -> total distance from mean

# Sort stocks by deviation from mean (insightful? Not really at all! but its just a start)
sorted_sD = sorted(squaredDistance.items(), key=operator.itemgetter(1))
sortedFrame = DataFrame(sorted_sD)
sortedFrame[1:10].plot(kind='barh')
sortedFrame[11:20].plot(kind='barh')

print 'Stocks organized by closest to mean'
for i in range(len(tickers)):
	print tickers[i].strip() + '  :  ' + str(squaredDistance[tickers[i].strip()])

print 'Top 20 stocks closest to the mean of the market:'
print str(sortedFrame[0:20])

#plt.show() # plot is useless right now
