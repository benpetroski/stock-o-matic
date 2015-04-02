import urllib

# Downloads the ticker symbols from finviz and prints the results to file (ticker_symbols.dat). This must be run before
# get_finviz_data.py.


# Number of stock can be found at finviz.com/screen.ashx
num_stocks = 7059


# Generate array of url ids (download in increments of 20)
nums = range(1, num_stocks, 20)
total_files = len(nums)


# Print stock names to file
fout = open('ticker_symbols.dat', 'w')
file_count = 1


# Loop through screen pages and parse for stock tickers
for num in nums:
    params = urllib.urlencode({'v': 111, 'r': num})
    f = urllib.urlopen("http://finviz.com/screener.ashx?%s" % params)

    # Open downloaded file and parse out the stock names
    data = f.read().replace('\n', '')

    # Loop through character by character and look for string
    first = True
    for ind, char in enumerate(data):
        if data[ind:ind+30] == "window.location='quote.ashx?t=":
            string = data[ind+30:ind+37]
            amp = string.index('&')

            quote = string[0:amp]
            fout.write(quote + '\n')
            if first:
                first_quote = quote
                first = False

    # Print out status
    print "File " + str(file_count) + " of " + str(total_files) + " parsed (" + first_quote + " to " + quote + ")"
    file_count += 1


# Clean up
fout.close()
