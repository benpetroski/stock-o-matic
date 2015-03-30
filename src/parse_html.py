import urllib

nums = range(1, 7060, 20)

for num in nums:
    print num
    urllib.urlretrieve("http://finviz.com/screener.ashx?v=111&r=" + str(num), "temp_" + str(num) + ".txt")


for num in nums:
    filename = 'temp_' + str(num) + '.txt'

    with open (filename, "r") as myfile:
        data = myfile.read().replace('\n', '')

        for ind, char in enumerate(data):
            if data[ind:ind+30] == "window.location='quote.ashx?t=":
                string = data[ind+30:ind+37]
                amp = string.index('&')
                
                print string[0:amp]
