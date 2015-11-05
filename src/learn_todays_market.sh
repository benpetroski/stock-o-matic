#! /bin/bash

# Learns stocks for the day, stores them on the pi

# Step 1: get all the ticker symbols (in case for some reason finviz adds or removes tickers day to day) - commented until devon fixes it
#python get_finviz_ticker_symbols.py;

# Step 2: get all the data from each stock and put them in the .dat file
python get_finviz_data.py;

# Step 3: Get the mean metrics
python learn_metrics.py;

# Step 4: Back up those metrics to a delicous mongoDB database!
python store_metrics.py; 