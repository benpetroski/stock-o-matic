import pymongo
from pymongo import Connection
import datetime
import sys

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

# prepare a simple apple query
stocks = []
variables = ['ticker:%s'%i for i in inputArgs]
for i, arg in enumerate(inputArgs):
	stock = {}
	stock['stockname'] = arg
	stocks.append(stock)

print stocks
for s in stocks:
	response = []
	for i in range(0, len(stringdates)):
		response.append(db[stringdates[i]].find(s)) # nice thing about mongodb - if the date doesn't exist as a collection name, find returns absolutely nothing!

	documents = []
	print s, 'query returns the following mongodb documents:'
	for j in range(len(response)):
		for document in response[j]:
		 	print(document)
		 	documents.append(document)

	print 'Stock prices for' , s, 'in reverse chronological order.'
	for i in range(len(documents)):
		print documents[i]['Price']
