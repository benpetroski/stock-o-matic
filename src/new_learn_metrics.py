#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import os


# our own module for connecting to the database
import dbinterface as dbi

# our own module with helper functions (just 2 right now)
import stockhelpers as stkh

# establish connection
# note: if id_rsa is not found, this might need to be changed.
path_to_rsa = os.path.expanduser("~/")
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

# clean up stuff - all this should be done far upstream
df.fillna(0) # fill NaN's with 0
df = df[df.stockname.notnull()] # remove any math NaN's
df = df[df.stockname != 'NaN'] # remove any personally placed NaN's
df = df[df.date.notnull()] # remove any math NaN's
df = df[df.date != 'NaN'] # remove any personally placed NaN's

# df = df[df.ROI != '-'] # remove any personally placed NaN's
# df = df[df.ROA != '-'] # remove any personally placed NaN's
# df = df[df['Perf Half Y'] != '-'] # remove any personally placed NaN's
# df = df[df['Change'] != '-'] # remove any personally placed NaN's
# df = df[df['Change'] != 'International, Inc.'] # remove any personally placed NaN's
# df.ROI.replace('%','',regex=True).astype('float')/100
# df.ROA.replace('%','',regex=True).astype('float')/100
# df['Perf Half Y'].replace('%','',regex=True).astype('float')/100
# df.Change.replace('%','',regex=True).astype('float')/100

'''data frames are excellent - and super fast! its essentially a machine version of 
an excel spreadsheet for example we can sort by any of the keys we want:'''

stkh.analyze_by_style(df, "highrisk")
stkh.analyze_by_style(df, "moderate")
stkh.analyze_by_style(df, "stable")
stkh.analyze_by_ab(df) # this one is still fishy due to annoying data cleaning issues

x = range(len(df))
y1 = df['ROI']
y2 = df['Perf Half Y']
y3 = df['ROA']
n = df['stockname']

plt.figure(1)
ax = plt.subplot(111)
ax.plot(x, y1, 'ko', x, y2, 'b*', x, y3, 'r^')
ax.annotate(n, xy=(x, y1), fontsize=10) # offset under, with very small font with ticker name
ax.annotate(n, xy=(x, y2), fontsize=10) # offset under, with very small font with ticker name
ax.annotate(n, xy=(x, y3), fontsize=10) # offset under, with very small font with ticker name
plt.legend(['ROI','Perf Half Y','ROA'])

ax.grid(True)
plt.show()


