#!/usr/bin/env python

import pandas as pd

# our own module for connecting to the database
import dbinterface as dbi

def get_metric(data, metricnames):
	metricdict = {}
	for i in range(len(metricnames)):
		try:
			metricdict[metricnames[i]] = [data[x][metricnames[i]] for x in range(len(data))]
		except KeyError:
			print "Metric name: " + metricnames[i] + " not found!!!"

	return metricdict

# establish connection
path_to_rsa = "/Users/chris/" # YOU NEED TO CHANGE THIS TO WHAT IT IS ON YOUR COMPUTER!!!!!!

# thanks to ben's work, this array can be as long or as short as you want it
stocknames = ["AAPL", "GOOG", "ANF", "SBUX", "NFLX", "LPCN", "GE", "HABT", "NOR", "BEBE", "WEET", "TCCO", "PEN"] # started just taking random ones i saw on finviz's homepage

# get a big array of dicts from the dict
alldata = dbi.get_stock_data(path_to_rsa, stocknames)

# this can be any or all metric names
metricnames = ["date", "stockname", "Price", "ROI", "ROA", "EPS next Y", "Volatility"]

# think vertical columns corresponding to a metric
metricwisearrays = get_metric(alldata, metricnames)

df = pd.DataFrame.from_dict(metricwisearrays)

'''data frames are excellent - and super fast! its essentially a machine version of 
an excel spreadsheet for example we can sort by any of the keys we want:'''


print "Sorted by date example:\n"
print df.sort('date', ascending=False) # most recent dates at top
print "\n\n\n"
'''you can also do multiple keys, and pandas will try to sort as best as possible. 
so i could imagine all the "good" metrics we want ascending and all the bad metrics as descending, for example:'''

print "Sorted by optimizing ROA and ROI, minimizing Volatility example:\n"
print df.sort(['ROA', 'ROI', 'Volatility'], ascending=[False, False, True]) # attempt to optimize 'good' metrics, minimize 'bad'

'''again, this stuff is hardcoded but we can abstract and revise to predifined parameters like we have with the rest of the code!!!!
i picture certain groups of metrics with the same analysis depending on what your investing style is or what kind of stock you are looking
to invest it... should be great'''

