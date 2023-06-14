from openbb_terminal.sdk import openbb
openbb.stocks.search(exchange_country="hong_kong")
#openbb.stocks.search(exchange= "hkg") #got [1645 rows x 6 columns]


"""
The problem is on line 217 in stocks_helper.py.
"""