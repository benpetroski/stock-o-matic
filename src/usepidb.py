import pymongo
from pymongo import Connection
import datetime
import sys
import matplotlib.pylab as plt

# NOTE: remember -- this script has to have the mongodb tunnel running in a SEPERATE terminal

# gets all input args. will have to enable capturing multiple tickers, 
# but for now it's just the one
inputArgs = []
for arg in sys.argv[1:]:
	inputArgs.append(arg)

# generate n number of days back (names of our collections in the mongodb
numdays = 365 # go back a year
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
stringdates = []
[stringdates.append(str(date_list[x]).split(" ")[0]) for x in range(0,len(date_list))] # clean them up a bit

# Our python client to the localhost mongodb
connection = Connection('localhost', 6789)

# Connect to the stockdata DB
db = connection['stockdata']

# List the collection names to see if we really are looking at the pi ones
print db.collection_names()

# queries for all input args
stocks = []
variables = ['ticker:%s'%i for i in inputArgs]
for i, arg in enumerate(inputArgs):
	stock = {}
	stock['stockname'] = arg
	stocks.append(stock)

count = 1
print stocks
for s in stocks:
	dates = []
	prices = []


	response = []
	for i in range(0, len(stringdates)):
		response.append(db[stringdates[i]].find(s)) # nice thing about mongodb - if the date doesn't exist as a collection name, find returns absolutely nothing!

	documents = []
	print s, 'query returns the following mongodb documents:'
	for j in range(len(response)):
		for document in response[j]:
		 	print(document)
		 	documents.append(document)
			dates.append(stringdates[j])


	print 'Stock prices for' , s, 'in reverse chronological order.'
	for i in range(len(documents)):
		print documents[i]['Price']
		prices.append(documents[i]['Price'])

	# make a simple plot for stock price vs time
	x = range(len(dates))
	axes = plt.figure(count).add_subplot(111)
	plt.title('Stock price for ' + s['stockname'])
	plt.plot(x, prices, 'ko-')
	plt.xlabel('Date [yyyy-mm-dd]')
	plt.ylabel('Stock Price [$]')
	plt.xticks(x, dates)
	count = count + 1


plt.show()


