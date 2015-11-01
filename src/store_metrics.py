import pymongo
from pymongo import Connection
import json
import glob
import datetime
import ntpath

# this script loops through all the .dat files for every stock and puts them in a tasty mongoDB database

# establish mongoDB connection
connection = Connection()

# today's timestamp will determine this particular db name's
today = str(datetime.date.today())

db = connection['stockdata']

import json
import glob
from pymongo import MongoClient

directory = '/Users/chris/github/stock-o-matic/src/finviz_scrape/data/*.dat'

print "Beginning backup..."
jsonFiles = glob.glob(directory)
for file in jsonFiles:
    datafile = open(file, 'r')
    stockname = ntpath.basename(file)
    stockname = stockname.split('.')[0] # get rid of the .dat ending
    data = datafile.read()
    mydict = eval(data) # eval the data (string type) to allow conversion to a python dictionary
    db[today].insert(mydict) # insert dict as a document in the mongoDB collection for today - pymongo handles the conversion to json by itself

print "Done."