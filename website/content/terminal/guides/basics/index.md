---
title: Basics
description: The OpenBB Terminal is a modern investment research platform for everyone. It is a desktop application that allows you to access all the data and tools you need to make better investment decisions.
keywords: [basics, installation, commands, menus, your own data, introduction, openbb terminal, explanation, basic usage, usage, how to]
---

The OpenBB Terminal is based off the <a href="https://en.wikipedia.org/wiki/Command-line_interface" target="_blank" rel="noreferrer noopener">Command Line Interface (CLI)</a>
which is installed by default on every computer. By opening the application you have installed from the [Installation Page](/terminal/quickstart/installation),
you are greeted with the following interface:

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/223211150-5c0bce44-98f3-403c-9db1-2344c1ad79d4.png"></img>

The OpenBB Terminal is centered around keyboard input. To navigate and perform analysis you will have to type in the name of the command followed by an `ENTER` (⏎). If you wish to see information about the OpenBB Terminal you can do so by typing `about` and then press `ENTER` (⏎). As you are typing, you will notice that you receive suggestions, by using the `DOWN` (⌄) arrow and pressing `ENTER` (⏎) you can select the command and execute it.

Throughout the entire terminal, the same set of colors are used which all share the same representation. This is structured as follows:

- <b><span style={{color:"#00AAFF"}}>Light Blue</span></b>: represents commands.
- <b><span style={{color:"#005CA9"}}>Dark Blue</span></b>: represents menus, also recognizable by the `>` in front.
- <b><span style={{color:"#EF7D00"}}>Orange</span></b>: represents titles and headers.
- <b><span style={{color:"#FCED00"}}>Yellow</span></b>: represents descriptions of a parameter or variable.
- <b>White</b>: represents text, usually in combination with a description that is in Yellow.

### Explanation of Menus

Menus, depicted in <b><span style={{color:"#005CA9"}}>Dark Blue</span></b>, take you to a new section of the terminal referred to as a menu. For example, if you wish to view information about stocks, you can do so by typing `stocks` and pressing `ENTER` (⏎). This opens a new menu as depicted below.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218974442-563cb216-623f-4f98-b2e1-9f1bb0e1a199.png"></img>

Depending on the menu you are in, you are presented with a new set of commands and menus you can select. There are interactions in place between each menu. For example, when selecting a company within the `stocks` menu, the terminal will remember your selection when you visit the `fa` or `options` menu. See [Introduction to Stocks](/terminal/guides/intros/stocks).

:::note **Pro tip:** you can quickly jump between menus by using a forward slash (`/`). For example, if I want to access the options menu, You can type `/stocks/options` to instantly arrive at this menu. You can do this from any location within the OpenBB Terminal!
:::

### Explanation of Commands

Commands, depicted in <b><span style={{color:"#00AAFF"}}>Light Blue</span></b>, execute an action or task. For example,
the commands that you are able to use from any menu in the terminal (see <a href="#explanation-of-menus">Explanation of Menus</a>) are as follows:

- `cls`: clears the screen, by executing this command you are left with an empty screen.
- `help`, `h` or `?`: displays the menu that you are currently on.
- `quit`, `q` or `..`: allows for navigation through the menu. E.g. if you type `stocks` press `ENTER` (⏎) and then
  use `q` and press `ENTER` (⏎) you return to where you started. Validate this by typing `?` and pressing `ENTER` (⏎).
- `support`: allows you to submit bugs, questions and suggestions.
- `about`: this opens the related guide, linking to this website. It also has the ability to open a guide to a specific
  command. For example, within the `stocks` menu, `about candle` opens <a href="/terminal/reference/stocks/candle/" target="_blank" rel="noreferrer noopener">this guide</a>.
- `wiki`: search for a given expression on the Wikipedia without leaving the terminal.

Continuing with the example mentioned at `quit`, revisit the `stocks` menu and look at the commands. At the top you will see a command named <a href="/terminal/reference/stocks/load" target="_blank" rel="noreferrer noopener">load</a>. To understand what this command can do, you can use `load -h` followed by `ENTER` (⏎). The `-h` stands for `help` and every command will have this feature. This will return the following:

```
usage: load [-t TICKER] [-s START] [-e END] [-i {1,5,15,30,60}] [-p] [-f FILEPATH] [-m] [-w] [--exchange] [--performance] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]]
            [--source {YahooFinance,AlphaVantage,Polygon,EODHD,Intrinio}]

Load stock ticker to perform analysis on. When the data source is yf, an Indian ticker can be loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in https://help.yahoo.com/kb/exchanges-data-
providers-yahoo-finance-sln2310.html.

optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2020-02-11)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock (default: 2023-02-15)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  -p, --prepost         Pre/After market hours. Only works for 'yf' source, and intraday data (default: False)
  -f FILEPATH, --file FILEPATH
                        Path to load custom file. (default: None)
  -m, --monthly         Load monthly data (default: False)
  -w, --weekly          Load weekly data (default: False)
  --exchange            Show exchange information. (default: False)
  --performance         Show performance information. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)
  --source {YahooFinance,AlphaVantage,Polygon,EODHD,Intrinio}
                        Data source to select from (default: YahooFinance)

For more information and examples, use 'about load' to access the related guide.

```

This shows you all **arguments** the command has. These are additional options you can provide to the command. Each default value is also displayed which is used when you do not select this option. For example, if I would use the <a href="https://www.investopedia.com/ask/answers/12/what-is-a-stock-ticker.asp" target="_blank" rel="noreferrer noopener">stock ticker</a> of Amazon (AMZN, which can also be found with `search amazon`), I can use `load AMZN` which will return the following:

```
(🦋) /stocks/ $ load AMZN

Loading Daily data for AMZN with starting period 2020-02-11.

```

The default values you see within `load -h` have been inputted here. E.g. the starting period is 2019-05-15. I can decide to change these default values by calling the argument and inputting a different value.

Whenever you wish to apply an optional argument, you use the related shortcode, e.g. `-s` or `--start`. Then, if there is an additional word behind the argument (in this case there is, which is `START`) it implies the argument expects you to define a value. Within the documentation you can read that the format must be `YYYY-MM-DD` implying that `2010-01-01` will be valid. If there is not an additional word behind it, it is enough to write down `load AMZN -p` (which refers to the prepost optional argument)

Let's change the starting and ending period of the data that is being loaded in by doing the following:

```
(🦋) /stocks/ $ load AMZN -s 2005-01-01 -e 2010-01-01

Loading Daily data for AMZN with starting period 2005-01-03.

```

We can check that this period has changed by looking into the <a href="https://www.investopedia.com/trading/candlestick-charting-what-is-it/" target="_blank" rel="noreferrer noopener">candle chart</a> with `candle`. This, again shares the same `-h` argument. This results in the following which indeed depicts our selected period.

```
(🦋) /stocks/ $ candle
```

![Candlestick Chart Amazon](https://user-images.githubusercontent.com/46355364/223211728-1317abea-36da-461c-bc3b-140ed7973173.svg)

As mentioned in the <a href="#explanation-of-menus">Explanation of Menus</a>, some information also transfers over to other menus and this includes the loaded market data from <a href="/terminal/reference/stocks/load" target="_blank" rel="noreferrer noopener">load</a>. So, if you would visit the `ta` menu (which stands for <a href="https://www.investopedia.com/terms/t/technicalanalysis.asp" target="_blank" rel="noreferrer noopener">Technical Analysis</a>) you will see that, by running any command, the selected period above is depicted again. Return to the Stocks menu again by using `q` and use it again to return to the home screen which can be shown with `?`.

### Expanding the Terminal with API keys
The OpenBB Terminal is built on a lot of different data sources. The example above collects data from Yahoo Finance. This could be undesirable and therefore we allow for a variety of different data sources. Think of Polygon, IEX Cloud, Alpha Vantage and Binance to name a few. Some of these sources require you to set an API Key to connect with their data.

:::note Setting API Keys
For an elaborate explanation of defining API keys to greatly extend the capabilities of the OpenBB Terminal, please have a look [**here**](/terminal/basics/advanced/api-keys).
:::

This becomes apparent when you receive a message like the following:

```
(🦋) /stocks/fa/ $ rot

API_FINNHUB_KEY not defined. Set API Keys in ~/.openbb_terminal/.env or under keys menu.
```

We ensure that any source has a (usually extensive) free tier before we include the source. For example, you will be able to obtain 30+ years of fundamental data and query extensive economic databases by collecting just a few of the API keys.

The [keys menu](/terminal/guides/advanced/api-keys) serves the purpose of providing you to set API keys so that this type of functionality becomes available. For example, in the case of `rot` you will see that the source is "FinnHub".

```
(🦋) /stocks/fa/ $ ?

╭───────────────────────────────────────────────────────────────────────────────── Stocks - Fundamental Analysis ─────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                 │
│     load               load a specific stock ticker for analysis                       [YahooFinance, AlphaVantage, Polygon, EODHD]                                                   │
│                                                                                                                                                                                                 │
│ Ticker: TSLA                                                                                                                                                                                    │
│                                                                                                                                                                                                 │
│ Company Overview:                                                                                                                                                                               │
│     enterprise         company enterprise value                                        [FinancialModelingPrep, YahooFinance]                                                                    │
│     overview           financial overview of the company                               [Finviz, FinancialModelingPrep, AlphaVantage, YahooFinance]                                              │
│     divs               show historical dividends for company                           [YahooFinance]                                                                                           │
│     splits             stock split and reverse split events since IPO                  [YahooFinance]                                                                                           │
│     rating             analyst prices and ratings over time of the company             [Finviz, FinancialModelingPrep]                                                                          │
│     rot                number of analyst ratings over time on a monthly basis          [Finnhub]                                                                                                │
│     score              value investing scores for any time period                      [FinancialModelingPrep]                                                                                  │
│     warnings           company warnings according to Sean Seah book                    [MarketWatch]                                                                                            │
│     sust               sustainability values (environment, social and governance)      [YahooFinance]
```

Therefore, you need to acquire an API key from FinnHub through the website and enter the key within the [keys menu](/terminal/advanced/api-keys).

### Importing and exporting data

Any type of data that you see within the OpenBB Terminal, you will be able to export to a variety of files like xlsx, csv and json.

:::note The OpenBBUserData Folder
All of the below examples are stored in the OpenBBUserData folder. This also applies to when you wish to import files, as is for example required within the [Portfolio menu](/terminal/guides/intros/portfolio). To find more information about this folder please have a look [**here**](/terminal/guides/advanced/data).
:::

For example, if you wish to download market data you can do so from the stocks menu with the following:

```console
/stocks/load AAPL -s 2010-01-01 --export xlsx
```

This results in the following:

![Export Example](https://user-images.githubusercontent.com/46355364/214817681-fd5324c3-003c-45eb-adf4-96d5b41a3c02.png)

We also allow you to define a file name, for example for the same stock tickers, we can also add in the filename. This time, we export to `csv`.

```console
/stocks/load AAPL -s 2010-01-01 --export apple.csv
```

Which results in the following:

![Filename Example](https://user-images.githubusercontent.com/46355364/214818131-597b3bd0-9c66-43f1-bf0e-2c0a703e2645.png)

Lastly, when you select the `xlsx` option, you can also specify the sheet name with `--sheet-name` which allows multiple datasets to be send to the same Excel file. Using the same stock ticker, we can define the following. First, get market data from the `stocks` menu:

```console
/stocks/load AAPL -s 2010-01-01 --export apple.xlsx --sheet-name Market Data
```

Then enter the `fa` (Fundamental Analysis) menu and type:

:::note 
This requires an API key from FinancialModelingPrep. Please have a look [here](https://docs.openbb.co/terminal/quickstart/api-keys).
:::

**Income Statement:**

```console
income --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Income Statement
```

**Balance Sheet:**
```console
balance --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Balance Sheet
```

**Cash Flow Statement:**

```console
cash --source FinancialModelingPrep -l 10 --export apple.xlsx --sheet-name Cash Flow Statement
```

This generates a file for Apple with market data from 2010-01-01 until now and income, balance and cash flow statements over the last 10 years as seen in the image below.

![Sheet Name Example](https://user-images.githubusercontent.com/46355364/214824561-6eaf3a88-746a-4abc-91e1-420c9036c00d.png)

Next to that, we also allow exporting to images, this can be PNG, JPG, PDF and SVG. For example, using our `portfolio` menu we can export the charts to any type of format which again can be found within the `OpenBBUserData` folder.

![image](https://user-images.githubusercontent.com/46355364/214819518-cec40468-9019-440c-8bfe-7bcabc207578.png)


It is also possible to use your own datastreams. It could be that you have a dataset in Microsoft Excel or similar that you would like to import for usage within any of our functionalities. Often functionalities will have a `--file` argument which refers to your own file.
