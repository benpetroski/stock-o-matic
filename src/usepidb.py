import pymongo
from pymongo import Connection
import datetime


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
query = {}
query['stockname'] = 'AAPL'

response = []
for i in range(0, len(stringdates)):
	response.append(db[stringdates[i]].find(query)) # nice thing about mongodb - if the date doesn't exist as a collection name, find returns absolutely nothing!

documents = []
print "Apple query returns the following mongodb documents:"
for i in range(len(response)):
	for document in response[i]:
	 	print(document)
	 	documents.append(document)

print "Stock prices for AAPL, in reverse chronological order (yes the last one is the price way back on april 2nd!)"
for i in range(len(documents)):
	print documents[i]["Price"]










