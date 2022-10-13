---
title: Introduction to the Stocks SDK
keywords: "stocks, stock, options, option, call, put, earnings, calendar, how-to, guide, scripts, fundamental, analysis, technical, behavioural, analyst, equity, research, api, sdk, application, python, notebook, jupyter"
excerpt: "This guide introduces the Stocks menu in the context of the OpenBB SDK."
geekdocCollapseSection: true
---

The <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Stocks menu</a> wraps all of the functions from the OpenBB Terminal application into a powerful SDK, enabling users to work with the data in a flexible environment that can be fully customized to meet the needs of any user. Code completion and contextual help makes the SDK is easy to use. Navigation is very similar to operating the CLI Terminal Application. 

## How to use the Stocks SDK

Start a Jupyter Notebook with as little as one line of code:

`from openbb_terminal.api import openbb`</br>

In the next cell, the code complete will activate after the `.` is entered, showing the submenus and functions at the root level of the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Stocks menu</a>.

![Stocks Menu](https://user-images.githubusercontent.com/85772166/195198260-fe1c4c65-2dc2-4001-94ff-f09e0b0ff431.png)

The contents of the menu is printed by running a cell with: `openbb.stocks`

![Stocks Menu](https://user-images.githubusercontent.com/85772166/195198410-0b44ee92-2c79-4efc-8490-a2de3173cfec.png)

Docstrings for each function are printed using the `help()` function of Python: `help(openbb.stocks.candle)`

![Calling the Help Dialogue](https://user-images.githubusercontent.com/85772166/195198556-29513bf4-896d-4d3c-be01-eeec8b05a9fa.png)

Add `%matplotlib inline` to the first cell for displaying charts in a Notebook file.

A candle chart is shown with: `openbb.stocks.candle(symbol = 'ticker')`. The contextual help shows the syntax and arguments for the function.

![Candle Function](https://user-images.githubusercontent.com/85772166/195198631-318fafcd-6fbf-4ce3-9ba9-2e94764020f4.png)

## Examples

Load historical price data into a Pandas DataFrame by declaring a name for the DataFrame:

`spy_monthly = openbb.stocks.load(symbol = 'SPY', start_date = '1990-01-01', monthly = True)`

![Load as a Pandas DataFrame](https://user-images.githubusercontent.com/85772166/195198733-cc819266-7e26-4870-83db-2c4d0ebaafdf.png)

Give the candle chart a custom title:

`openbb.stocks.candle(data = spy_monthly, symbol = 'SPY - Monthly Candles')`

![Change the Chart Title](https://user-images.githubusercontent.com/85772166/195198857-9af40ffe-e7b6-46d3-9887-bca05999fd3f.png)

Get the options data for a specific expiration date:

![Options Chains](https://user-images.githubusercontent.com/85772166/195199095-93657a4a-80b9-4a7b-a462-f7c6507558f0.png)

Search for a company with the `search` function:

`openbb.stocks.search(sector = 'Energy', country = 'United Kingdom', query = 'oil')`

![Stocks Search](https://user-images.githubusercontent.com/85772166/195199177-57eeeba7-72ca-4f5b-a88c-67e35398cace.png)

Screen stocks reporting earnings this week:

`earnings_calendar = openbb.stocks.disc.upcoming(limit = 1)`</br>
`earnings_tickers = list(earnings_calendar.Ticker)`</br>
`earnings_screener = openbb.stocks.ca.screener(similar = earnings_tickers, data_type = 'valuation')`</br>
`pd.DataFrame(earnings_screener).sort_values(by = 'P/B')`</br>

![Earnings Screener](https://user-images.githubusercontent.com/85772166/195199267-5e30550e-5b31-4615-ad7a-48348040103b.png)

Have you created a script using the OpenBB SDK? Show us your examples on social media!
