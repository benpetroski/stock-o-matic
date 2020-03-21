#!/usr/bin/python

import sys
import json
from FinvizTicker import FinvizTicker

stockData = FinvizTicker(sys.argv[1])
with open('/Users/chris/projects/stock-o-matic/src/stock-jarvis/data/metrics.json', 'w') as f:
    json.dump(stockData.metrics, f)
