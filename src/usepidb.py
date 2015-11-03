import pymongo
from pymongo import Connection

# Our python client to the localhost mongodb
connection = Connection('localhost', 6789)

# Connect to the stockdata DB
db = connection['stockdata']

# List the collection names to see if we really are looking at the pi ones
print db.collection_names() 

query = {}
query['stockname'] = 'AAPL'
response = db['stockdata'].find({"stockname":"AAPL"})













