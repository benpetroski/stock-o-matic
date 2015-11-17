#!/usr/bin/env python

import pandas as pd

# our own module for connecting to the database
import dbinterface as dbi

# our own module with helper functions (just 2 right now)
import stockhelpers as stkh

# establish connection
path_to_rsa = "/Users/chris/" # YOU NEED TO CHANGE THIS TO WHAT IT IS ON YOUR COMPUTER!!!!!!
dbi.connect(path_to_rsa)

# thanks to ben's work, this array can be as long or as short as you want it
#stockNames = ["AAPL", "GOOG", "ANF", "SBUX", "NFLX", "LPCN", "GE", "HABT", "NOR", "BEBE", "WEET", "TCCO", "PEN"] # started just taking random ones i saw on finviz's homepage
stockNames = stkh.get_ticker_names()

# get a big list of dicts representing all data we have on the mongodb
allData = dbi.get_all_stock_data()

# this can be any or all metric names
#metricnames = ["date", "stockname", "Price", "ROI", "ROA", "EPS next Y", "Volatility"]
metricNames = stkh.get_metric_names() # get ALL the metric names!!!

metricNames.extend(["date", "stockname"])

# think vertical columns corresponding to a metric
metricArrays = stkh.get_metric_as_array(allData, metricNames)

df = pd.DataFrame.from_dict(metricArrays)

'''data frames are excellent - and super fast! its essentially a machine version of 
an excel spreadsheet for example we can sort by any of the keys we want:'''

stkh.analyze_by_style(df, "highrisk")

stkh.analyze_by_style(df, "moderate")

stkh.analyze_by_style(df, "moderate")

#stkh.analyze_by_ab(df) # this one is still under construction due to annoying data cleaning issues

'''again, this stuff is hardcoded but we can abstract and revise to predifined parameters like we have with the rest of the code!!!!
i picture certain groups of metrics with the same analysis depending on what your investing style is or what kind of stock you are looking
to invest it... should be great'''

