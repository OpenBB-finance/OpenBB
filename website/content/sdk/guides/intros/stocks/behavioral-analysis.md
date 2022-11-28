---
title: Behavioral Analysis
keywords:
  [
    "stocks", "stock", "options", "option", "call", "put"
  ]
excerpt: "This guide introduces the BA menu in the context of the OpenBB SDK."
---

The BA module provides programmatic access to the commands from within the OpenBB Terminal. Import the OpenBB SDK module, and then access the functions similarly to how the Terminal menus are navigated. The code completion will be activated upon entering `.`, after, `openbb.ba`
​

## How to Use

​
The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:
​

```python
from openbb_terminal.sdk import openbb
```

​
A brief description below highlights the main Functions and Modules available in the BA SDK

| Path                       |    Type    |                                  Description |
| :------------------------- | :--------: | -------------------------------------------: |
| openbb.stocks.ba.bullbear         |  Function  |                     Estimate Quick Sentiment |
| openbb.stocks.ba.headlines        |  Function  |            Sentiment from 15+ News Headlines |
| openbb.stocks.ba.spacc            |  Function  | Shows SPAC announcements from SPAC subreddit |
| openbb.stocks.ba.watchlist        |  Function  |                 Show Other User's Watchlists |
| openbb.stocks.ba.messages         |  Function  |         Output last 30 messages on the board |
| openbb.stocks.ba.mentions         |  Function  |         Interest Over Time Based on Mentions |
| openbb.stocks.ba.hist             |  Function  |                  Plot Historical RHI and AHI |
| openbb.stocks.ba.snews            |  Function  |           Stock Price Plotted Over Sentiment |
| openbb.stocks.ba.redditsent       |  Function  |        Search for Tickers and Find Sentiment |
| openbb.stocks.ba.popular          |  Function  |                         Show Popular Tickers |
| openbb.stocks.ba.spac             |  Function  |        Shows Other User's SPAC Announcements |
| openbb.stocks.ba.getdd            |  Function  |                            Get Due Diligence |
| openbb.stocks.ba.regions          |  Function  |         Regions Showing the Highest Interest |
| openbb.stocks.ba.trending         |  Function  |                              Trending Stocks |
| openbb.stocks.ba.wsb              |  Function  |                Highlights from WSB Subreddit |
| openbb.stocks.ba.queries          |  Function  |                          Top Related Queries |
| openbb.stocks.ba.sentiment        |  Function  |  Stock Sentiment Prediction from Last Tweets |
| openbb.stocks.ba.infer            |  Function  |             Stock Sentiment from Last Tweets |
| openbb.stocks.ba.stalker          |  Function  |                    Stocktwit's last messages |
| openbb.stocks.ba.rise             |  Function  |                   Top Rising Related Queries |

Alteratively you can print the contents of the BA SDK with:

```python
help(openbb.stocks.ba)
```

## Examples

### headlines

Sentiment from over 15 news headlines for each day. This data can be used for further analysis of the stock

```python
openbb.stocks.ba.headlines("TSLA")
```

| date                |   Sentiment Analysis |
|:--------------------|---------------------:|
| 2022-11-09 00:00:00 |                0.209 |
| 2022-11-10 00:00:00 |               -0.025 |
| 2022-11-11 00:00:00 |                0.027 |
| 2022-11-14 00:00:00 |               -0.402 |
| 2022-11-15 00:00:00 |               -0.122 |
| 2022-11-16 00:00:00 |               -0.35  |
| 2022-11-17 00:00:00 |                0.156 |
| 2022-11-18 00:00:00 |                0.216 |
| 2022-11-21 00:00:00 |               -0.071 |
| 2022-11-22 00:00:00 |               -0.003 |

### regions

See the top regions where a stock is searched

```python
openbb.stocks.ba.regions("TSLA")
```

| geoName                                |   TSLA |
|:---------------------------------------|-------:|
| Canada                                 |    100 |
| United States                          |     95 |
| Singapore                              |     94 |
| Estonia                                |     51 |
| Taiwan                                 |     50 |
| Slovenia                               |     40 |
| Switzerland                            |     36 |
| Denmark                                |     36 |
| New Zealand                            |     33 |
| Sweden                                 |     31 |
| Finland                                |     24 |
| Australia                              |     24 |
| Belgium                                |     22 |
| Czechia                                |     20 |
| Bulgaria                               |     18 |
| United Arab Emirates                   |     17 |
| United Kingdom                         |     15 |
| Portugal                               |     12 |
| Austria                                |     11 |
| Romania                                |     10 |
| South Africa                           |      7 |
| Saudi Arabia                           |      7 |
| Germany                                |      7 |
| Argentina                              |      6 |
| Spain                                  |      6 |
| France                                 |      4 |
| Colombia                               |      4 |
| Philippines                            |      4 |
| Brazil                                 |      4 |
| Thailand                               |      4 |
| Poland                                 |      3 |
| Vietnam                                |      2 |
| Russia                                 |      2 |
| Turkey                                 |      2 |
| Pakistan                               |      0 |

### rise

See which search queries are popular right now

```python
openbb.stocks.ba.rise("AAPL")
```

|    | query           |   value |
|---:|:----------------|--------:|
|  0 | nio             |  220300 |
|  1 | nio stock       |  106650 |
|  2 | pltr stock      |   64750 |
|  3 | mrna stock      |   59750 |
|  4 | nio stock price |   53450 |
|  5 | zm stock        |   49500 |
|  6 | bynd            |   44850 |
|  7 | pltr            |   41000 |
|  8 | spce            |   37350 |
|  9 | zm              |   31650 |
