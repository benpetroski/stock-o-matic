#! /bin/bash
# ben is probably going to rage at using a shell script, 
# but hey, a true programmer chooses the correct tool for the correct job
# this will soon be moved to a raspberry pi or similiar to be croned after the closing bell each day
# and the day's data put on a mysql table

# Step 1: get all the ticker symbols (incase for some reason finviz adds or removes tickers day to day) - commented until devon fixes it
#python finviz_scrape/get_finviz_ticker_symbols.py;

# Step 2: get all the data from each stock and put them in the .dat file
python finviz_scrape/get_finviz_data.py;

# Step 3: Get the mean metrics
python learn_metrics.py;

# Step 4: Back up those metrics to a delicous mongoDB database!
python store_metrics.py; 