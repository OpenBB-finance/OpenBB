---
title: Basics
sidebar_position: 1
---
### Importing the SDK

Now that you have the SDK installed, the first step is to import the OpenBB SDK in your preferred code editor. Nearly everything required to interact with any function from the OpenBB Terminal gets imported in one line. Begin a Python script or Notebook file with:

```python
from openbb_terminal.sdk import openbb
```

Example snippets used in the remainder of this guide will assume the code block above is used.

### Navigation

In the same way as operating the OpenBB Terminal, functions are divided into menus which are scrollable after importing into a jupyter notebook. Entering a period, `.`, after `openbb`, will display the Sub-menus available.

![Navigation](https://user-images.githubusercontent.com/85772166/202795900-5f1cb00a-a0ff-4899-b6e2-c5af54b653d1.png "Navigation")

An alternate way to view the contents of a menu is to use Python's built-in help.

```python
help(openbb.stocks.dd)
```

### Docstrings

In addition to Python's built-in help, docstrings are also displayed in the Contextual Help window, within a Jupyter environment or by running `help(openbb.economy.events)` in your code editor.

```python
help(openbb.economy.events)

Help on Operation in module openbb_terminal.core.library.operation:

<openbb_terminal.core.library.operation.Operation object>
    Get economic calendar for countries between specified dates

    Parameters
    ----------
    countries : [List[str],str]
        List of countries to include in calendar.  Empty returns all
    start_date : str
        Start date for calendar
    end_date : str
        End date for calendar

    Returns
    -------
    pd.DataFrame
        Economic calendar
```

## How to use the SDK

### Your First Function

To get started using the OpenBB SDK you can try the below code for your first function.

```python
openbb.economy.events()
```

|     | Time (GMT) | Country        | Event                         | actual | consensus | previous | Date       |
| --: | :--------- | :------------- | :---------------------------- | :----- | :-------- | :------- | :--------- |
|   0 | 01:30      | France         | French Unemployment Rate      | 7.3%   | 7.3%      | 7.4%     | 2022-11-15 |
|   1 | 02:00      | United Kingdom | Average Earnings ex Bonus     | 5.7%   | 5.5%      | 5.5%     | 2022-11-15 |
|   2 | 02:00      | United Kingdom | Average Earnings Index +Bonus | 6.0%   | 5.9%      | 6.1%     | 2022-11-15 |
|   3 | 02:00      | United Kingdom | Claimant Count Change         | 3.3K   | 17.3K     | 3.9K     | 2022-11-15 |
|   4 | 02:00      | United Kingdom | Employment Change 3M/3M       | -52K   | -25K      | -109K    | 2022-11-15 |

:::note - The results from data functions are not stored to memory unless explicitly instructed to. Most functions returning data are presented as a Pandas DataFrame.
:::

Modify the syntax slightly to deliver the output into a DataFrame:

```python
economic_calendar = openbb.economy.events()
```

Defined as a variable, interacting with the results becomes a matter of manipulating tables. For example, the code block below will filter the results of the events function to display only events scheduled at a specific time.

```python
economic_calendar = openbb.economy.events()
economic_calendar.set_index(keys = ['Time (GMT)'], append = True, inplace = True)
events = economic_calendar.filter(like = '9:00', axis = 0)

events
```

|       | Country       | Event                                  | actual | consensus | previous | Date       |
| :---- | :------------ | :------------------------------------- | :----- | :-------- | :------- | :--------- |
| 09:00 | United States | Fed Governor Cook Speaks               | -      | -         | -        | 2022-11-15 |
| 09:00 | Germany       | German Buba Balz Speaks                | -      | -         | -        | 2022-11-15 |
| 09:00 | Germany       | German Buba Vice President Buch Speaks | -      | -         | -        | 2022-11-15 |

### Passing Results to Another Function

Let's take a look at another example where the input to a function is a list. It may be desirable to derive that list from a different function. This can be useful for screening tickers, or analyzing particular industries or sectors. The Comparison Analysis sub-module, within Stocks, is one set of functions that can benefit from this kind of workflow. Instead of something like:

```python
openbb.stocks.ca.screener(similar = ['AAPL', 'NFLX', 'META', 'AMZN', 'MSFT', 'GOOGL', 'DIS', 'TSLA'], data_type = 'valuation')
```

Try, `openbb.etf.holdings`, to populate a list dynamically:

```python
symbols = openbb.etf.holdings('DIA')
dia_symbols = list(symbols.index.drop(['N/A']))
dia_valuation = openbb.stocks.ca.screener(similar = dia_symbols, data_type = 'valuation')
dia_valuation = dia_valuation.sort_values(by = ['Price'], ascending = False).convert_dtypes()

dia_valuation.head(5)
```

|     | Ticker | Market Cap |   P/E | Fwd P/E | PEG  |  P/S | P/B     |   P/C |  P/FCF | EPS this Y | EPS next Y | EPS past 5Y | EPS next 5Y | Sales past 5Y |  Price |  Change |  Volume |
| --: | :----- | ---------: | ----: | ------: | :--- | ---: | :------ | ----: | -----: | ---------: | ---------: | ----------: | ----------: | ------------: | -----: | ------: | ------: |
|  25 | UNH    | 5.0033e+11 | 25.17 |   20.61 | 1.77 | 1.59 | 6.43    | 12.88 |  19.61 |      0.128 |     0.1315 |       0.201 |      0.1422 |         0.092 | 503.01 | -0.0209 | 5007787 |
|  10 | GS     |  1.282e+11 | 10.18 |   10.17 | N/A  | 2.08 | 1.24    |  0.45 |   2.98 |      1.403 |     0.0976 |       0.296 |     -0.0912 |         0.113 | 382.88 |  0.0014 | 3184768 |
|  11 | HD     | 3.1097e+11 | 18.86 |   17.86 | 1.2  |    2 | 1334.43 |   247 |  89.72 |      0.301 |     0.0361 |       0.192 |       0.157 |         0.098 | 311.93 |  0.0163 | 9239159 |
|   1 | AMGN   | 1.5543e+11 | 22.86 |    15.4 | 3.38 |  5.9 | 41.77   | 13.54 |  32.04 |     -0.165 |     0.0486 |       0.001 |      0.0677 |         0.025 |  283.6 |  -0.006 | 2761083 |
|  18 | MCD    | 2.0272e+11 |  34.3 |   26.01 | 5.14 | 8.71 | N/A     | 71.67 | 118.65 |      0.591 |     0.0522 |        0.13 |      0.0667 |        -0.012 | 267.84 | -0.0163 | 5421817 |


### Displaying Charts

The OpenBB SDK has built-in charting libraries for Matplotlib, for any chart available from the Terminal. User style sheets can be added to the folder (more on this in [Importing and Exporting Data](/sdk/guides/advanced/data)), `~/OpenBBUserData/styles/user`. Styles are shared properties between the OpenBB Terminal and the SDK.

:::note Displaying charts in Jupyter Notebooks requires an additional line of code. You can either render a static image with `%matplotlib inline` or add in pan/zoom functionality with `%matplotlib widget`.
:::

Functions, such as `candle`, exist to display charts. Others, like those within the Technical Analysis module, have the option to return either, a chart or raw data. The next examples will outline a few different scenarios. First, let's get some data:

```python
spy_daily = openbb.stocks.load(
        symbol = 'SPY',
        start_date = '1993-11-01',
        monthly = True)
```

Data from the previous example, `spy_daily`, can be used in the `openbb.stocks.candle` function, for example:

```python
openbb.stocks.candle(
    data = spy_daily,
    asset_type = 'SPY - Monthly Chart from November, 1993',
    symbol = ''
)
```

![openbb.stocks.candle](https://user-images.githubusercontent.com/85772166/202801049-083ec045-7038-440b-8a54-7a02269e4a40.png "openbb.stocks.candle")

The function will also respond to individual tickers without saving the data first as done with `load`:

```python
openbb.stocks.candle('SPY')
```

![openbb.stocks.candle](https://user-images.githubusercontent.com/85772166/203477909-6a97175b-b3e3-4236-9753-609895c6aa69.png "openbb.stocks.candle")

Where functions in the Terminal display either a chart or raw data, the command will have an additional `_chart` component. For example, Donchian Channels:

```python
openbb.ta.donchian(openbb.stocks.load('SPY', interval = 15))
```

| date                | DCL_20_20 | DCM_20_20 | DCU_20_20 |
| :------------------ | --------: | --------: | --------: |
| 2022-11-15 14:45:00 |    394.49 |    398.33 |    402.17 |
| 2022-11-15 15:00:00 |    394.49 |   398.195 |     401.9 |
| 2022-11-15 15:15:00 |    394.49 |   398.195 |     401.9 |
| 2022-11-15 15:30:00 |    394.49 |   398.105 |    401.72 |
| 2022-11-15 15:45:00 |    394.49 |   398.027 |   401.565 |

```python
openbb.ta.donchian_chart(
    data = openbb.stocks.load('SPY', interval = 15),
    symbol = 'SPY 15 Minute Data'
)
```

![openbb.ta.donchian](https://user-images.githubusercontent.com/85772166/202802907-40fa97c8-055d-4ef5-bbc2-7f01a5c5b738.png "openbb.ta.donchian")

Futures curves are another example where this syntax is applied:

```python
openbb.futures.curve_chart('GE')
```

![openbb.futures.curve](https://user-images.githubusercontent.com/85772166/201583945-18364efa-c305-4c1a-a032-f779e28894c8.png "openbb.futures.curve")

The intros section for each module explore further functionality and provide sample code snippets. For example, an introduction to Stocks can be found [here](/sdk/guides/intros/stocks).
