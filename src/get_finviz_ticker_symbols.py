import requests
import urllib
from BeautifulSoup import BeautifulSoup
from multiprocessing import Pool

# Downloads the ticker symbols from finviz and prints the results to file (ticker_symbols.dat). This must be run before
# get_finviz_data.py.

def get_script(pgnum):
    # Download the ticker, and parse using beautiful soup
    params = urllib.urlencode({'v': 111, 'r': pgnum})
    html = requests.get("http://finviz.com/screener.ashx?%s" % params)
    data = BeautifulSoup(html.content)

    # Get the main table and remove the first header row
    table = data.find('table', {'bgcolor': '#d3d3d3'})
    rows = table.findAll('tr')
    rows.pop(0)

    # Extract the second column from the table
    stock = []
    for row in rows:
        # Extracts the columns of each row
        cols = row.findAll('td')
        link = cols[1].findAll('a')
        stock.append(str(link[0].text))

    return stock

# Download an example page to parse the total number of stocks
html = requests.get("http://finviz.com/screener.ashx")
data = BeautifulSoup(html.content)
num = str(data.findAll('td', {'class': 'count-text', 'width': '140'})[0].text)
num_stocks = int(num[6:-3])

# Generate array of url ids (download in increments of 20)
nums = range(1, num_stocks+1, 20)
total_files = len(nums)

# Start 20 processes, as they empty, a new case is fed in
pool = Pool(processes=20)
tickers = pool.map(get_script, nums)

# Write the stocks to file
fout = open('ticker_symbols.dat', 'w')
for chunk in tickers:
    for ticker in chunk:
        fout.write('%s\n' % ticker)
fout.close()
