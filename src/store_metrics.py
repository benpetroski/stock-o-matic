import subprocess
import time
import pymongo
from pymongo import Connection
import json
import glob
import datetime
import ntpath
import dbinterface as dbi

# this script loops through all the .dat files for every stock and puts them in the tasty raspberry pi mongoDB database

# before sending data to the mongodb, we need to connect to it!
path_to_rsa = "/Users/chris/" # YOU NEED TO CHANGE THIS TO WHAT IT IS ON YOUR COMPUTER!!!!!!
dbi.connect(path_to_rsa)

# Our python client to the localhost mongodb
connection = Connection('localhost', dbi.__dbport__) # we can call __dbport__ since it is a global variable in dbinterface.py

# today's timestamp will determine this particular db name's
today = str(datetime.date.today())

db = connection['stockdata']

directory = '/Users/chris/github/stock-o-matic/src/data/*.dat'

print "Beginning backup to raspberry pi..."
jsonFiles = glob.glob(directory)
for file in jsonFiles:
    datafile = open(file, 'r')
    stockname = ntpath.basename(file)
    stockname = stockname.split('.')[0] # get rid of the .dat ending
    data = datafile.read()
    try:
    	mydict = eval(data) # eval the data (string type) to allow conversion to a python dictionary
    except SyntaxError:
    	print "EOF crap... no clue... for stock..." + stockname
    mydict['date'] = today # fix for the issue before!
    mydict['stockname'] = stockname # fix for the issue before!
    if 'Oper. Margin' in mydict.keys():
    	mydict['Oper Margin'] = mydict.pop('Oper. Margin')
    db[today].insert(mydict) # insert dict as a document in the mongoDB collection for today - pymongo handles the conversion to json by itself

print "Done."