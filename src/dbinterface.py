#!/usr/bin/env python

# imports
import os
import time
import pymongo
from pymongo import Connection
import datetime
from sshtunnel import SSHTunnelForwarder

# I made the port a global variable, if we may ever want to change it
global __dbport__
__dbport__ = 6789

def connect(path_to_rsa):

	print "Attempting to connect with the mongodb server on chris's rapsberry pi...\n"
	server = SSHTunnelForwarder(('chrisfrew.in', 8022),\
		ssh_username="pi",\
		ssh_private_key=path_to_rsa + ".ssh/id_rsa",\
		local_bind_address=('0.0.0.0', __dbport__),\
		remote_bind_address=('127.0.0.1', 27017))
	server.start()
	time.sleep(3)
	print "\nConnection successfully established.\n"


# this is the current bottleneck of our code - querying the mongodb to get the responses for each stock of interest
# not sure if sshtunnel forward is thread safe but we could potentially open multiple ports to complete the read
def get_stock_data(stocknames):

	print "Pulling stock data; this can take a while...\n"
	# generate n number of days back (names of our collections in the mongodb
	numdays = 60 # go back two months
	base = datetime.datetime.today()
	date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
	stringdates = []
	[stringdates.append(str(date_list[x]).split(" ")[0]) for x in range(0,len(date_list))] # clean them up a bit

	# Our python client to the localhost mongodb
	connection = Connection('localhost', __dbport__)
	# Connect to the stockdata DB
	db = connection['stockdata']

	count = 1
	documents = []
	for stock in stocknames:

		responses = []
		for i in range(0, len(stringdates)):
			response = db[stringdates[i]].find({"stockname" : stock}).count()
			if response != 0: # don't append to array if mongodb didn't return anything
				responses.append(db[stringdates[i]].find({"stockname" : stock})) # nice thing about mongodb - if the date doesn't exist as a collection name, find returns absolutely nothing!

		for i in range(len(responses)):
			for document in responses[i]:
				document['date'] = stringdates[i] # NOTE: this is currently a patch for what should be done when the data is read!
			 	documents.append(document)

		print "Done with pulling stock " + stock + " (" + str(count) + " of " + str(len(stocknames)) + ")"
		count = count + 1

	if len(documents) == 0:
		print "Warning: no documents were found in for the given stock names!"

	print "Done.\n"

	return documents

def get_all_stock_data():

	print "Pulling all stock data; this can take a few seconds...\n"
	# generate n number of days back (names of our collections in the mongodb
	numdays = 60 # go back two months
	base = datetime.datetime.today()
	date_list = [base - datetime.timedelta(days=x) for x in range(0, numdays)]
	stringdates = []
	[stringdates.append(str(date_list[x]).split(" ")[0]) for x in range(0,len(date_list))] # clean them up a bit

	# Our python client to the localhost mongodb
	connection = Connection('localhost', __dbport__)
	# Connect to the stockdata DB
	db = connection['stockdata']

	documents = []

	responses = []
	for i in range(0, len(stringdates)):
		response = db[stringdates[i]].find().count()
		if response != 0: # don't append to array if mongodb didn't return anything
			responses.append(db[stringdates[i]].find()) # nice thing about mongodb - if the date doesn't exist as a collection name, find returns absolutely nothing!

	for i in range(len(responses)):
		for document in responses[i]:
			document['date'] = stringdates[i] # NOTE: this is currently a patch for what should be done when the data is read!
		 	documents.append(document)

	if len(documents) == 0:
		print "Warning: no documents were found!"

	print "Done.\n"

	return documents

