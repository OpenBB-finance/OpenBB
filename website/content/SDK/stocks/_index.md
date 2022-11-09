---
title: Introduction to the Stocks Menu
keywords: "stocks, stock, options, option, call, put, earnings, calendar, how-to, guide, scripts, fundamental, analysis, technical, behavioural, analyst, equity, research, api, sdk, application, python, notebook, jupyter"
excerpt: "This guide introduces the Stocks menu in the context of the OpenBB SDK."
geekdocCollapseSection: true
---
The capabilities of the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Stocks menu</a> from the OpenBB Terminal are wrapped into a powerful SDK, enabling users to work with the data in a flexible environment that can be fully customized to meet the needs of any user. Code completion and contextual help makes it easy to use. Navigating is very similar to operating the CLI Terminal Application.

## How to use

Start a Python script or Notebook file by importing the module:

`from openbb_terminal.sdk import openbb`

In the next cell, code completion will activate after the `.` is entered, showing the submenus and functions at the root level of the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Stocks menu</a>.

![Stocks Menu](https://user-images.githubusercontent.com/85772166/195393178-83c39078-3419-4fae-bf69-5950b143b422.png)

The contents of the menu is printed by running a cell with: `openbb.stocks`

![Stocks Menu](https://user-images.githubusercontent.com/85772166/195393891-8ff6d5d2-043a-463b-994a-2ad0805bef0d.png)

Docstrings for each function are printed using the `help()` function of Python: `help(openbb.stocks.candle)`

![Calling the Help Dialogue](https://user-images.githubusercontent.com/85772166/195407824-16ce6a84-ca1f-42ea-9a4e-7de6584b356c.png)

Add `%matplotlib inline` to the first cell for displaying charts within a Notebook file.

A candle chart is shown with: `openbb.stocks.candle(symbol = 'ticker')`. The contextual help provides syntax and arguments for the function.

![Candle Function](https://user-images.githubusercontent.com/85772166/195409395-4a09d357-9725-4e71-8342-86607f27d060.png)

## Examples

Pass historical price data to a Pandas DataFrame by declaring a name for the DataFrame:

`spy_monthly = openbb.stocks.load(symbol = 'SPY', start_date = '1990-01-01', monthly = True)`

![Load to a Pandas DataFrame](https://user-images.githubusercontent.com/85772166/195410451-7ab90457-122e-478c-a023-72fdf31fd6f5.png)

Give the candle chart a custom title:

`openbb.stocks.candle(data = spy_monthly, symbol = 'SPY - Monthly Candles')`

![Change the Chart Title](https://user-images.githubusercontent.com/85772166/195198857-9af40ffe-e7b6-46d3-9887-bca05999fd3f.png)

Get the options data for a specific expiration date:

![Options Chains](https://user-images.githubusercontent.com/85772166/195446332-58daf843-ff1b-4821-a12e-a15209397af0.png)

Search for companies with the `search` function:

`openbb.stocks.search(sector = 'Energy', country = 'United Kingdom', query = 'oil')`

![Stocks Search](https://user-images.githubusercontent.com/85772166/195447185-d3582665-7852-4a1e-bf0e-d0d389ec8ed7.png)

Make a custom screener for tickers on the most Stocktwits users' watchlists:
````
stocktwits = openbb.stocks.ba.trending()
stocktwits = pd.DataFrame(stocktwits).sort_values(by = 'Watchlist Count', ascending = False)
tickers = list(stocktwits.Ticker)
stocktwits.head(5)

screener_results = openbb.stocks.ca.screener(similar = tickers, data_type = 'overview')
pd.DataFrame(screener_results).sort_values(by = 'Market Cap')
````
![Comparing Trending Tickers From Stocktwits](https://user-images.githubusercontent.com/85772166/195452365-44847886-02c8-4b0f-a348-7eeb791b8f60.png)
