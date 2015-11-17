#!/usr/bin/env python

# Imports
import os.path
from pandas import DataFrame
import numpy as np
import operator
import matplotlib.pyplot as plt

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

# Open output files - put them right with the other stocks so they will be added as document on the mongoDB database
g = open('data/meanmetrics.dat', 'w')
h = open('data/meandistance.dat', 'w')
q = open('data/top50.dat', 'w')

meanMetricDict = {}
squaredDistanceDict = {}
top50Dict = {}

# this are important for catologuing them into the mongoDB database - we can look them up quickly - i think its also a good idea to store a 'version' to know at what point our machine learning algorithm was at
meanMetricDict['metrictype'] = 'meanmetrics'
meanMetricDict['version'] = 'v1'
squaredDistanceDict['metrictype'] = 'meandistance'
squaredDistanceDict['version'] = 'v1'
top50Dict['metrictype'] = 'top50'
top50Dict['version'] = 'v1'

# Read in ticker symbol list as created by get_finviz_ticker_symbols.py
with open('ticker_symbols.dat') as f:
    tickers = f.readlines()

# Read in metric names
with open('metrics.dat') as f:
    metricNames = f.readlines()

# Create metrics python dict
metrics = {}
for i in range(len(tickers)):
	fname = 'data/' + tickers[i].rstrip() + '.dat'
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
		fname = 'data/' + tickers[j].rstrip() + '.dat'
		if(os.path.isfile(fname)):
			tickers[j] = tickers[j].strip() # remove newline
			metricNames[i] = metricNames[i].strip() # remove newline
			if metricNames[i] == 'Sales Q/Q1':
				metricNames[i] = 'Sales Q/Q' # the weird fix
			if metricNames[i] == 'Oper. Margin':
				metricNames[i] = 'Oper Margin' # another fix
			if tickers[j] in tickersFrame.keys(): # make sure we actually have that ticker (again... devon's fault)
				# Skip null values, stock indexs (NASDAQ, SP500, etc) (basically this if statement is to filter out any non-number metrics or wacky ones i didn't feel like fixing)
				if metricNames[i] not in tickersFrame[tickers[j]].keys():
					continue # skip this one! 


				if tickersFrame[tickers[j]][metricNames[i]] != '-' \
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
					if hasNumbers(fixedstr) and fixedstr != ' Advantage Municipal Fund 2' and fixedstr != ' Advantage Municipal Fund 3':
						metricSum = metricSum + float(fixedstr.replace(',','')) # given a metric, loop over all stocks, strip % and convert to float!
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
	meanMetricDict[metricNames[i].strip()] = str(meanMetrics[i])

# Now a very simple calculation of squared distance to the mean
squaredDistance = {}
for i in range(len(tickers)):
	squaredDistanceSum = 0
	for j in range(len(metricNames)):
		fname = 'data/' + tickers[i].rstrip() + '.dat'
		if(os.path.isfile(fname)):
			if metricNames[j] not in tickersFrame[tickers[i]].keys():
					continue # skip this one! 
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
				if hasNumbers(fixedstr) and fixedstr != ' Advantage Municipal Fund 2' and fixedstr != ' Advantage Municipal Fund 3':
					squaredDistanceSum = squaredDistanceSum + (meanMetrics[j] - float(fixedstr.replace(',','')))**2 # We have the name indice in the squareddistance vector just for reference at the end

	squaredDistance[tickers[i].strip()] = squaredDistanceSum # create dictionary of stockname -> total distance from mean

# Sort stocks by deviation from mean (insightful? Not really at all! but its just a start)
sorted_sD = sorted(squaredDistance.items(), key=operator.itemgetter(1))
sortedFrame = DataFrame(sorted_sD)
sortedFrame[1:10].plot(kind='barh')
sortedFrame[11:20].plot(kind='barh')

print 'Stocks organized by closest to mean:'
for i in range(len(tickers)):
	print tickers[i].strip() + '  :  ' + str(squaredDistance[tickers[i].strip()])
	squaredDistanceDict[tickers[i].strip()] = str(squaredDistance[tickers[i].strip()])

print 'Top 50 stocks closest to the mean of the market:'

for i in range(50):
	print sortedFrame.iloc[i][0] + " : " + str(sortedFrame.iloc[i][1])
	top50Dict[sortedFrame.iloc[i][0]] = sortedFrame.iloc[i][1]

# write the python dicts to the files
g.write(str(meanMetricDict))
h.write(str(squaredDistanceDict))
q.write(str(top50Dict))

# close the files
g.close()
h.close()
q.close()
