#!/usr/bin/env python

import pandas as pd

def get_ticker_names():
	# Read in ticker symbol list as created by get_finviz_ticker_symbols.py
	with open('data/ticker_symbols.dat') as f:
	    tickers = f.readlines()

	tickers[:] = [x.rstrip("\n") for x in tickers]
	return tickers

def get_metric_names():
	# Read in metric names
	with open('data/metrics.dat') as f:
	    metricNames = f.readlines()

	metricNames[:] = [x.rstrip("\n") for x in metricNames]
	return metricNames

def get_metric_as_array(data, metricnames):
	metricdict = {}
	for i in range(len(metricnames)):
		mymetriclist = [] # prepare a list for each metric
		for j in range(len(data)):
			try:
				mymetriclist.append(data[j][metricnames[i]])
			except KeyError:
				mymetriclist.append('NaN')
				print("Metric name: " + metricnames[i] + " not found in stock! Appending 'NaN' in this metric list and moving to next metric!")
		metricdict[metricnames[i]] = mymetriclist # append list to the dictionary with the current metric as key
	return metricdict

def analyze_by_style(df, style):

	# for high risk high reward style of investing
	if style == "highrisk":
		print("Highrisk style:")
		# most recent dates at top (yes this is hardcoded i couldn't get eval to friggin work)
		print(df.sort(['Volatility', 'Beta', 'Volume'], ascending=[True, True, True])[:20])
		print("\n\n\n")

	# for a moderately style of investing
	if style == "moderate":
		print("Moderate style:")
		 # most recent dates at top
		print(df.sort(['Perf Week', 'ROA', 'ROI', 'Volatility', 'Volume'], ascending=[True, True, True, False, True])[:20])
		print("\n\n\n")

	# for very stable style of investing
	if style == "stable":
		print("Stable style:")
		# most recent dates at top
		print(df.sort(['Volatility', 'Beta', 'Volume'], ascending=[False, False, True])[:20])
		print("\n\n\n")


# as i was saying now that we have a dataframe we can prototype here with a bunch of different data science methods
def analyze_by_ab(df):
	# this is an A/B test... i use the metric "Change" as my A/B: the stocks that changed positive, and those that changed negative

	print("Running A/B analysis... this takes a while")

	for i in range(len(df)):
		
		if type(df['Change'].iloc[i]) != float: # first make sure it is not a float already
			try: # now convert percentages to floats
				df['Change'].iloc[i] = float(df['Change'].iloc[i].strip('%'))  # parsed percentages
			except ValueError:
				df['Change'].iloc[i] = 0
			except AttributeError:
				continue

	posStocks = df[df['Change'] > 0]
	negStocks = df[df['Change'] < 0]
	posMean = posStocks.mean()
	negMean = negStocks.mean()

	print("Means of stocks that rose:")
	print(posMean)
	print("\n\n\n")
	print("Means of stocks that fell:")
	print(negMean)


def analyze_by_ndspace(df):
	print("nothing here yet!")
	return df

def analyze_by_kmeans(df):
	print("nothing here yet!")
	return df









