import requests
import urllib
from bs4 import BeautifulSoup
from multiprocessing import Pool

# Downloads the ticker symbols from finviz and prints the results to file (data/ticker_symbols_lists/ticker_symbols.dat). This must be run before
# get_finviz_data.py.
def get_table_column(page_num):
    # Download the ticker, and parse using beautiful soup
    params = urllib.parse.urlencode({'v': 111, 'r': page_num})
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36"}
    response = requests.get("https://finviz.com/screener.ashx?%s" % params, headers=headers)
    data = BeautifulSoup(response.content, 'html.parser')

    # initialize stocks array
    stocks = []

    # print current page of total (total from page scrape)
    # total = data.find('td', {'class': 'count-text'})
    # if total is not None:
    #     print(str(page_num) + " of " + total.split(' ')[1] + " tickers...")

    # Get the main table and remove the first header row
    table = data.find('table', {'class': 'screener_table'})
    if table is not None:
        rows = table.findAll('tr')
        rows.pop(0)

        # Extract the second column from the table
        for row in rows:
            # Extracts the columns of each row
            cols = row.findAll('td')
            link = cols[1].findAll('a')
            stocks.append(str(link[0].text))
        
        # print the stocks we just got
        print(stocks)
    else:
        print("damn, table is NoneType!")
        # print url we are currently on
        print("https://finviz.com/screener.ashx?%s" % params)
        # print(response.content)

    return stocks

if __name__ == '__main__':
    # Download an screen page to determine the total number of stocks
    # Simulate that my macbook pro is doing this with headers :)
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36"}
    response = requests.get("https://finviz.com/screener.ashx", headers=headers)
    data = BeautifulSoup(response.content, 'html.parser')
    element = data.find('div', {'id': 'screener-total'})
    total_text = element.text.strip()
    num_stocks = total_text.split()[-2]

    # Convert to int
    num_stocks = int(num_stocks)

    # Generate array of url params for starting index of stock i.e. https://finviz.com/screener.ashx?v=111&r=61
    nums = range(1, num_stocks+1, 20)

    # Start processes, as they empty, a new case is fed in
    # Processes may need to be tuned to prevent being rate limited by finviz
    pool = Pool(processes=1)
    tickers = pool.map(get_table_column, nums)

    # Write the stocks to file
    with open('data/ticker_symbols_lists/ticker_symbols.dat', 'w') as fp:
        for chunk in tickers:
            for ticker in chunk:
                fp.write('%s\n' % ticker)

