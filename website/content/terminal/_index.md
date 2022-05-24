---
title: Getting started with the OpenBB Terminal
keywords: "getting started, beginner guide, how to use openbb, openbb keys, openbb terminal, openbb"
excerpt: "This page guides you how to use the OpenBB terminal, developed by OpenBB."
geekdocCollapseSection: true
---
## Introduction

OpenBB is a leading open source investment analysis company. We represent millions of investors who want to leverage
state-of-the-art data science and machine learning technologies to make sense of raw unrefined data. Our mission
is to make investment research effective, powerful and accessible to everyone.

---
<center><b><span style="color:#00AAFF">If you are new to the terminal, please continue reading this </span>
<span style="color: white">Getting Started page</span>
<span style="color:#00AAFF">that explains how the terminal works. To get an understanding
of each menu (e.g. <a href="stocks" style="color: white">stocks</a>
or <a href="economy" style="color: white">economy</a>) 
visit the related introduction page.</span></b></center>

---

### Why Python?

Python is one of the most used programming languages due to its simplified syntax and shallow learning curve.
On top of this, it is highly used in data science and academia world (particularly on finance, economics
or business related degrees). This is very important, as it is the first time in history that users - regardless
of their background - can so easily add features to an investment research platform.

The OpenBB Terminal provides a modern Python-based integrated environment for investment research, that allows an
average joe retail trader to leverage state-of-the-art Data Science and Machine Learning technologies.  As a modern
Python-based environment, the OpenBB Terminal opens access to numerous Python data libraries in Data Science (Pandas,
Numpy, Scipy, Jupyter), Machine Learning (Pytorch, Tensorflow, Sklearn, Flair), and Data Acquisition (Beautiful Soup,
and numerous third-party APIs).

### Why Open Source?

An open source product allows for higher quality, greater reproducibility, lower costs, more transparency,
and faster go-to-market due to the strong community created. In addition, users can adapt the platform to their
needs or even build proprietary features on top of our infrastructure - which ultimately can result in a marketplace.

The OpenBB Terminal empowers individuals, regardless of whether they want to invest on the stock market in Japan,
invest real estate in Portugal or invest in the cryptomarket, to contribute and share their passion, dreams and desires
about the OpenBB Terminal. This brings together contributors that are not only software engineers but also financial
advisors, data scientists, machine learning researchers, analysts, day traders, mathematicians, academics, physicists
and portfolio managers.

## Accessing the OpenBB Terminal

The OpenBB Terminal can be directly installed on your computer via our installation program. Within this section, you 
are guided through the installation process and how to launch the program. If you are a developer, please have a 
look <a href="https://github.com/OpenBB-finance/OpenBBTerminal" target="_blank">here</a>. If you struggle with the
installation process, please don't hesitate to reach us on <a href="https://discord.gg/Xp7PrCUj" target="_blank">Discord</a>
or visit our <a href="https://openbb.co/contact" target="_blank">contact page</a>.

### Installation for Windows

The process starts off by downloading the installer, see below for how to download the most recent release:

1. Go to <a href="https://github.com/OpenBB-finance/OpenBBTerminal/releases" target="_blank">the following link</a>
2. Click on the 'Latest' release and scroll down
3. Click on the ".exe" file, this downloads the installation program

When the file is downloaded, you can follow the following steps:

| Installation instructions                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Illustration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Double click the .exe file that got downloaded to your "Downloads" folder. You will most likely receive the error on the right stating "Windows protected your PC". This is because the installer is still in beta phase, and the team has not yet requested verification from Windows. <br></br> Click on "More info" and select "Run anyway" to start the installation process. Proceed by following the steps. Do note that if you wish to install the application to 'Program Files' that you will have to run the resulting application as Administrator. <br></br> By clicking on the application that appeared on your Desktop, you are able to run the Terminal. The first time this takes a bit longer to load. | <p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502271-69ad8075-165f-4b1a-8ab8-254d643a5dae.png"><img width="500" alt="windows_protected_your_pc" src="https://user-images.githubusercontent.com/46355364/169502271-69ad8075-165f-4b1a-8ab8-254d643a5dae.png"></a></p><p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502143-ba88de53-7757-48f2-9ec4-748d4917044b.png"><img width="500" alt="run_anyway" src="https://user-images.githubusercontent.com/46355364/169502143-ba88de53-7757-48f2-9ec4-748d4917044b.png"></a></p><p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502187-f4e42333-a947-464b-9320-a8f63c7ce089.png"><img width="500" alt="run_the_terminal" src="https://user-images.githubusercontent.com/46355364/169502187-f4e42333-a947-464b-9320-a8f63c7ce089.png"></a></p> |

### Installation for macOS

The process starts off by downloading the installer, see below for how to download the most recent release:

1. Go to <a href="https://github.com/OpenBB-finance/OpenBBTerminal/releases" target="_blank">the following link</a>
2. Click on the 'Latest' release and scroll down
3. Click on the ".dmg" file, this downloads the installation program

Installation instructions:

1. Open the .dmg file that got downloaded to your "Downloads" folder.
2. Drag the folder into your "Applications" folder. This should take some time as it is extracting the
   files from the .dmg file.
3. Open the folder and click on the "OpenBB Terminal" file, this should run the application.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502594-5cafd088-01bc-49fb-9c70-a9105798e9f9.png"><img width="800" alt="mac_os_installation" src="https://user-images.githubusercontent.com/46355364/169502594-5cafd088-01bc-49fb-9c70-a9105798e9f9.png"></a>

| Note about "Cannot check it for malicious software" warning                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Illustration                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Run the file. You will most likely receive a message that macOS was not able to check whether the application contains malicious software. This is because the installer is still in beta phase, and the team has not yet requested verification from Apple. See below how to correct for this. <br></br> Go to `System Preferences > Security & Privacy > General`. You should see a message at the bottom that says that the file "was blocked from use because it is not from an identified developer". Click on “Allow anyway” or "Open anyway". <br></br> You should now be able to launch the application. | <p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502740-2345e2d6-1230-427d-afbc-58f9a30c4803.png"><img width="500" alt="malicious_software_warning" src="https://user-images.githubusercontent.com/46355364/169502740-2345e2d6-1230-427d-afbc-58f9a30c4803.png"></p></a><p align="center"><a target="_blank" href="https://user-images.githubusercontent.com/46355364/169502720-e28c78c5-7684-45a9-aafc-cf497de38c09.png"><img width="500" alt="warning_fix" src="https://user-images.githubusercontent.com/46355364/169502720-e28c78c5-7684-45a9-aafc-cf497de38c09.png"></p></a> |

## Structure of the OpenBB Terminal

The OpenBB Terminal is based off the <a href="https://en.wikipedia.org/wiki/Command-line_interface" target="_blank">Command Line Interface (CLI)</a>
which is installed by default on every computer. By opening the application you have installed via "Accessing the OpenBB Terminal",
you are greeted with the following interface:

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/169503071-ffb2d88d-0786-4568-94c0-ad55c8f8f3e7.png"><img src="https://user-images.githubusercontent.com/46355364/169503071-ffb2d88d-0786-4568-94c0-ad55c8f8f3e7.png" alt="Main Menu" width="800"/></a>

The OpenBB Terminal is centered around keyboard input. To navigate and perform analysis you will have to type in the name of the command followed by an `ENTER` (⏎). If you wish to see information about the OpenBB Terminal you can do so by typing `about` and then press `ENTER` (⏎). As you are typing, you will notice that you receive suggestions, by using the `DOWN` (⌄) arrow and pressing `ENTER` (⏎) you can select the command and execute it.

Throughout the entire terminal, the same set of colors are used which all share the same representation. This is structured as follows:
- <b><span style="color:#00AAFF">Light Blue</span></b>: represents commands.
- <b><span style="color:#005CA9">Dark Blue</span></b>: represents menus, also recognizable by the `>` in front.
- <b><span style="color:#EF7D00">Orange</span></b>: represents titles and headers.
- <b><span style="color:#FCED00">Yellow</span></b>: represents descriptions of a parameter or variable.
- <b>White</b>: represents text, usually in combination with a description that is in Yellow.

### Explanation of Menus

Menus, depicted in <b><span style="color:#005CA9">Dark Blue</span></b>, take you to a new section of the terminal referred
to as a menu. For example, if you wish to view information about stocks, you can do so by typing `stocks` and pressing `ENTER` (⏎).
This opens a new menu as depicted below.

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/169503240-922357c8-5e2b-41f0-aca2-c1fc849dcd1c.png"><img src="https://user-images.githubusercontent.com/46355364/169503240-922357c8-5e2b-41f0-aca2-c1fc849dcd1c.png" alt="Stocks Menu" width="800"/></a>

Depending on the menu you are in, you are presented with a new set of commands (see "Explanation of Commands")
and menus you can select. There are interactions in place between each menu. For example, when selecting a company within
the `stocks` menu, the terminal will remember your selection when you visit the `fa` or `options` menu.
See <a href="stocks" target="_blank">Introduction to Stocks</a> for more information.

### Explanation of Commands

Commands, depicted in <b><span style="color:#00AAFF">Light Blue</span></b>, execute an action or task. For example,
the commands that you are able to use from any menu in the terminal (see "Explanation of Menus") are as follows:

- `cls`: clears the screen, by executing this command you are left with an empty screen.
- `help`, `h` or `?`: displays the menu that you are currently on. 
- `quit`, `q` or `..`: allows for navigation through the menu. E.g. if you type `stocks` press `ENTER` (⏎) and then
use `q` and press `ENTER` (⏎) you return to where you started. Validate this by typing `?` and pressing `ENTER` (⏎).
- `support`: allows you to submit bugs, questions and suggestions.

Continuing with the example mentioned at `quit`, revisit the `stocks` menu and look at the commands. At the top you 
will see a command named <a href="stocks/load" target="_blank">load</a>. To understand what this command can do, you can use `load -h` followed by `ENTER` (⏎). The `-h` stands for `help` and every command will have this feature. This will return the following:

```
2022 May 19, 05:27 (🦋) /stocks/ $ load -h
usage: load [-t TICKER] [-s START] [-e END] [-i {1,5,15,30,60}] [--source {yf,av,iex,polygon}] [-p] [-f FILEPATH] [-m] [-w] [-r {ytd,1y,2y,5y,6m}] [-h]

Load stock ticker to perform analysis on. When the data source is syf', an Indian ticker can be loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.

optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2019-05-15)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock (default: 2022-05-19)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  --source {yf,av,iex,polygon}
                        Source of historical data. (default: yf)
  -p, --prepost         Pre/After market hours. Only works for 'yf' source, and intraday data (default: False)
  -f FILEPATH, --file FILEPATH
                        Path to load custom file. (default: None)
  -m, --monthly         Load monthly data (default: False)
  -w, --weekly          Load weekly data (default: False)
  -r {ytd,1y,2y,5y,6m}, --iexrange {ytd,1y,2y,5y,6m}
                        Range for using the iexcloud api. Note that longer range requires more tokens in account (default: ytd)
  -h, --help            show this help message (default: False)
```

This shows you all **arguments** the command has. These are additional options you can provide to the command. Each
default value is also displayed which is used when you do not select this option. For example, if I would use the <a href="https://www.investopedia.com/ask/answers/12/what-is-a-stock-ticker.asp" target="_blank">stock ticker</a>
of Amazon (AMZN, which can also be found with `search amazon`), I can use `load AMZN` which will return the following:

```
2022 May 19, 05:27 (🦋) /stocks/ $ load AMZN

Loading Daily AMZN stock with starting period 2019-05-15 for analysis.

Datetime: 2022 May 19 05:33
Timezone: America/New_York
Currency: USD
Market:   OPEN
Company:  Amazon.com, Inc.

                                           AMZN Performance
┏━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ 1 Day   ┃ 1 Week ┃ 1 Month  ┃ 1 Year   ┃ YTD      ┃ Volatility (1Y) ┃ Volume (10D avg) ┃ Last Price ┃
┡━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ -3.34 % │ 1.65 % │ -32.26 % │ -33.71 % │ -37.14 % │ 31.36 %         │ 5.51 M           │ 2142.25    │
└─────────┴────────┴──────────┴──────────┴──────────┴─────────────────┴──────────────────┴────────────┘
```

The default values you see within `load -h` have been inputted here. E.g. the starting period is 2019-05-15. I can 
decide to change these default values by calling the argument and inputting a different value. Let's change the starting 
and ending period of the data that is being loaded in by doing the following:

```
2022 May 19, 05:38 (🦋) /stocks/ $ load AMZN -s 2005-01-01 -e 2010-01-01

Loading Daily AMZN stock with starting period 2005-01-01 for analysis.

Datetime: 2022 May 19 05:43
Timezone: America/New_York
Currency: USD
Market:   OPEN
Company:  Amazon.com, Inc.

                                           AMZN Performance
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ 1 Day   ┃ 1 Week  ┃ 1 Month ┃ 1 Year   ┃ Period   ┃ Volatility (1Y) ┃ Volume (10D avg) ┃ Last Price ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ -3.51 % │ -3.18 % │ -2.87 % │ 162.32 % │ 203.73 % │ 49.78 %         │ 8.53 M           │ 134.52     │
└─────────┴─────────┴─────────┴──────────┴──────────┴─────────────────┴──────────────────┴────────────┘
```

We can check that this period has changed by looking into the <a href="https://www.investopedia.com/trading/candlestick-charting-what-is-it/" target="_blank">candle chart</a> with `candle`. This, again shares the same `-h` argument. This results in the following which indeed depicts our
selected period.

```
2022 May 19, 05:44 (🦋) /stocks/ $ candle
```
<a target="_blank" href="https://user-images.githubusercontent.com/46355364/169503345-a9409637-dc7a-4193-9c87-38b1b6ee1a08.png"><img src="https://user-images.githubusercontent.com/46355364/169503345-a9409637-dc7a-4193-9c87-38b1b6ee1a08.png" alt="Amazon Candle Chart" width="800"/></a>

As mentioned in the "Explanation of Menus", some information also transfers over to other menus and this includes the
loaded market data from <a href="stocks/load" target="_blank">load</a>.
So, if you would visit the `ta` menu (which stands for <a href="https://www.investopedia.com/terms/t/technicalanalysis.asp" target="_blank">Technical Analysis</a>) you will see that, by running any command, the selected period above is depicted again. Return to the Stocks menu again by using `q` and use it again to return to the home screen which can be shown with `?`.

## Accessing other sources of data via API keys

Within this menu you can define your, often free, API key from various platforms like Alpha Vantage, FRED, IEX, Twitter, DeGiro, Binance and Coinglass. API keys are in essence a set of random characters that is unique to you.

You can access this menu from the homepage with `keys` which will open the menu as shown below:

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/169802651-6e752a4c-9cfd-4ce1-a99c-978eee5a0aca.png"><img src="https://user-images.githubusercontent.com/46355364/169802651-6e752a4c-9cfd-4ce1-a99c-978eee5a0aca.png" width="800"/></a>

Within this menu you are able to set your API keys to access the commands that require that key. You can do so by typing the command followed by the API key, for example: `fred a215egade08a8d47cfd49c849658a2be`. When you press `ENTER` (⏎) the terminal will test whether this API key works. If it does, you receive the message `defined, test passed` and if it does not, you receive the message `defined, test failed`.

To figure out where you can obtain the API key, you can enter the command (e.g. `av`) and press `ENTER` (⏎) or use the table below. **We recommend that you gradually obtain and set keys whenever you wish to use features that require an API key. For example, if you are interested in viewing recent news about a company, you should set the API key from the 'News API'.**

| Command    | Name                                     | URL                                                                                |
|:-----------|:-----------------------------------------|:-----------------------------------------------------------------------------------|
| av         | AlphaVantage                             | https://www.alphavantage.co/support/#api-key                                       |
| fmp        | Financial Modelling Prep                 | https://site.financialmodelingprep.com/developer/docs/                             |
| quandl     | Quandl                                   | https://www.quandl.com                                                             |
| polygon    | Polygon                                  | https://polygon.io                                                                 |
| fred       | Federal Reserve Economic Database (FRED) | https://fred.stlouisfed.org                                                        |
| news       | News API                                 | https://newsapi.org/                                                               |
| tradier    | Tradier                                  | https://developer.tradier.com                                                      |
| cmc        | CoinMarketCap                            | https://coinmarketcap.com/                                                         |
| finnhub    | Finnhub                                  | https://finnhub.io/                                                                |
| iex        | IEX Cloud                                | https://iexcloud.io/                                                               |
| reddit     | Reddit                                   | https://www.reddit.com/wiki/api                                                    |
| twitter    | Twitter                                  | https://developer.twitter.com                                                      |
| rh         | Robinhood                                | https://robinhood.com/us/en/                                                       |
| degiro     | DeGiro                                   | https://www.degiro.com/                                                            |
| oanda      | Oanda                                    | https://developer.oanda.com                                                        |
| binance    | Binance                                  | https://binance.com                                                                |
| bitquery   | Bitquery                                 | https://bitquery.io/                                                               |
| si         | Sentiment Investor                       | https://sentimentinvestor.com                                                      |
| cb         | Coinbase                                 | https://help.coinbase.com/en/exchange/managing-my-account/how-to-create-an-api-key |
| walert     | Whale Alert                              | https://docs.whale-alert.io/                                                       |
| glassnode  | Glassnode                                | https://docs.glassnode.com/basic-api/api-key#how-to-get-an-api-key/                |
| coinglass  | Coinglass                                | https://coinglass.github.io/API-Reference/#api-key                                 |
| ethplorer  | Ethplorer                                | https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API                           |
| smartstake | Smartstake                               | https://www.smartstake.io                                                          |
| github     | GitHub                                   | https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api           |

## Available menus

There is a large collection of (sub) menus available. Here, the asset class and other menus are described. To find a  detailed description and explanation of its usage for each menu, click on the corresponding link to visit the introduction page.

The asset class menus are as follows:
   
- <a href="stocks" target="_blank">Introduction to Stocks</a>: access historical pricing data, options, sector and 
industry analysis, and overall due diligence.
- <a href="cryptocurrency" target="_blank">Introduction to Crypto</a>: dive into onchain data, tokenomics, circulation supply,
nfts and more.
- <a href="etf" target="_blank">Introduction to ETF</a>: explore exchange traded funds, historical pricing, holdings
and screeners.
- <a href="forex" target="_blank">Introduction to Forex</a>: see foreign exchanges, quotes, forward rates for currency
pairs and Oanda integration.
- <a href="funds" target="_blank">Introduction to Funds</a>: discover mutual funds, general overviews, holdings and
sector weights.

The other menus are as follows:
   
- <a href="economy" target="_blank">Introduction to Economy</a>: explore global macroeconomic data including 
interest and inflation rates, GDP and its components, futures, yield curves and treasury rates.
- <a href="alternative" target="_blank">Introduction to Alternative</a>: explore alternative datasets such as COVID and
open source metrics.
- <a href="econometrics" target="_blank">Introduction to Econometrics</a>: perform (advanced) regression techniques and
statistical tests on custom datasets to understand relationships for both time series and panel data.
- <a href="portfolio" target="_blank">Introduction to Portfolio</a>: understand how your portfolio evolved over time, what
assets contributed the most to this performance, compare this to a benchmark and make adjustments via various portfolio
optimization techniques.
- <a href="jupyter" target="_blank">Introduction to Dashboards</a>: see interactive dashboards using voila and
jupyter notebooks.
- <a href="reports" target="_blank">Introduction to Reports</a>: create customizable research reports through
jupyter notebooks.

To adjust the lay-out and settings of the OpenBB Terminal you can access the `settings` menu. This menu allows you to
tweak how the terminal behaves. For example, you are able to define the coloring, interactive graphs and whether to use
pretty tables.

## Obtaining support and/or giving feedback

Being an open source platform that wishes to tailor to the needs of any type of investor, we highly encourage anyone 
to share with us their experience and/or how we can further improve the OpenBB Terminal. This can be anything
from a very small bug to a new feature to the implementation of a highly advanced Machine Learning model.

You are able to directly send us information about a bug or question/suggestion from inside the terminal by using
the `support` command which is available everywhere in the terminal. Here you can select which command you want to
report a bug, ask a question or make a suggestion on. When you press `ENTER` (⏎), you are taken to the Support form
which is automatically filled with your input. You are only required to include the type (e.g. bug, suggestion or
question) and message in the form although this can also be set directly from inside the terminal (see `support -h`).

<a target="_blank" href="https://user-images.githubusercontent.com/46355364/169503483-c93c83fa-e9e9-4345-b816-8fcfe02b6785.png"><img src="https://user-images.githubusercontent.com/46355364/169503483-c93c83fa-e9e9-4345-b816-8fcfe02b6785.png" alt="Support Command" width="800"/></a>

Alternatively, you can contact us via the following routes:
   
- If you notice that a feature is missing inside the terminal, please fill in the <a href="https://openbb.co/request-a-feature" target="_blank">Request a Feature form</a>.
- If you wish to report a bug, have a question/suggestion or anything else, please fill in the <a href="https://docs.google.com/forms/d/e/1FAIpQLSe0-HKitlJMtTO9C2VR7uXVtTzmQgiyE1plf3nEkYCRx6WGRg/viewform" target="_blank">Support form</a>.
- If you wish to speak to us directly, please contact us via <a href="https://discord.gg/Xp7PrCUj" target="_blank">Discord</a>.
