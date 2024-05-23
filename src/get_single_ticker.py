#!/usr/bin/env python

from FinvizTicker import FinvizTicker

# first argument is the ticker
import sys
ticker = sys.argv[1]

FinvizTicker(ticker)