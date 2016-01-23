#!/usr/bin/env python

# imports
import Quandl
import matplotlib.pyplot as plt

# read in the API key (don't want it on the public repo)
f = open('/home/chris/.ssh/quandl_key.txt', 'r') # everyone should put this in the same directory as the id_rsa file we have for the mongodb
key = f.read().rstrip() # the txt file is a single line containing the key. Will remove any whitespace following, if any
f.close() # close the file

# retrieve data
data1 = Quandl.get("WIKI/AAPL", authtoken=key) # I believe the "WIKI" is all data provided by Quandl for the given stock. DATA is a DataFrame type
data2 = Quandl.get("WIKI/GOOG", authtoken=key) # I believe the "WIKI" is all data provided by Quandl for the given stock. DATA is a DataFrame type

# plot data
plt.figure(1)
plt.plot(data1['Close']) # plots the date (x axis) versus the closing value (y axis) 
plt.plot(data2['Close']) 
plt.legend(['AAPL', 'GOOG'])
plt.show() # show the plot!
