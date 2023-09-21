---
title: Technical Analysis
keywords: [technical, analysis, ta, t/a, intraday, daily, indicators, signals, average, moving, exponential, rsi, fibonacci, retracement, bollinger, heltner, accumulation, distribution, obv, on-balance, volume, volatility, trend, momentum, overlap, crypto, stocks, funds, etf, etfs, realized, fx, forex]
description: An introduction to the Technical Analysis menu of the OpenBB Terminal.  This guide provides an overview of the functions and provides examples for use.
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Technical Analysis - Terminal | OpenBB Docs" />

The Technical Analysis menu offers the user a suite of tools for analyzing the technical components of an asset's trading history. The menu can be found in most wings of the Terminal:

- [Crypto](https://docs.openbb.co/terminal/usage/intros/crypto)
- [Stocks](https://docs.openbb.co/terminal/usage/intros/stocks)
- [ETF](https://docs.openbb.co/terminal/usage/intros/etf)
- [Forex](https://docs.openbb.co/terminal/usage/intros/forex)

The commands are divided by categories that define their purpose for general-use:

- Overlap - Moving averages
- Momentum - Oscillating signals
- Trend - Directional strength
- Volatility - Width of the price bands
- Volume - Singling out volume
- Custom - Multiple indicators and Fibonacci retracements

All commands in this menu will rely on the interval and window chosen when loading an asset for analysis.  Refer to the directory tree on the left side of the page, [here](https://docs.openbb.co/terminal/reference), for information on individual commands. To get a better understanding of what these features are, and the formulas behind them, a number of sources should be consulted; but, a good starting point is [Investopedia](https://www.investopedia.com/terms/t/technicalanalysis.asp).  The menu employs the [Pandas-TA Library](https://github.com/twopirllc/pandas-ta).  Submit a [feature request](https://openbb.co/request-a-feature) to let us know which indicators we should add next!

### How to Use

To begin, enter the menu from one of the menus listed above by entering `ta`.  For demonstration purposes, we will use `QQQ` as the ticker.  Let's grab some data!

```console
/stocks/load QQQ/ta
```

The block above loads daily QQQ historical prices and volume, then enters the Technical Analysis menu.  The table below lists all the available analysis functions.

| Function Key | Type       |                                 Description |
| :----------- | :--------- | ------------------------------------------: |
| load         | -          |             Load a new ticker for analysis. |
| ema          | Overlap    |                 Exponential Moving Average. |
| hma          | Overlap    |                        Hull Moving Average. |
| sma          | Overlap    |                      Simple Moving Average. |
| wma          | Overlap    |                    Weighted Moving Average. |
| vwap         | Overlap    |              Volume Weighted Average Price. |
| zlma         | Overlap    |                    Zero-Lag Moving Average. |
| cci          | Momentum   |                    Commodity Channel Index. |
| cg           | Momentum   |                          Center of Gravity. |
| clenow       | Momentum   |        Clenow Volatility Adjusted Momentum. |
| demark       | Momentum   |          Tom Demark's Sequential Indicator. |
| macd         | Momentum   |      Moving Average Convergence/Divergence. |
| fisher       | Momentum   |                           Fisher Transform. |
| rsi          | Momentum   |                    Relative Strength Index. |
| stoch        | Momentum   |                      Stochastic Oscillator. |
| adx          | Trend      |         Average Directional Movement Index. |
| aroon        | Trend      |                            Aroon Indicator. |
| atr          | Volatility |                         Average True Range. |
| bbands       | Volatility |                            Bollinger Bands. |
| cones        | Volatility |                  Realized Volatility Cones. |
| donchian     | Volatility |                          Donchian Channels. |
| kc           | Volatility |                           Keltner Channels. |
| ad           | Volume     |             Accumulation/Distribution Line. |
| adosc        | Volume     |                         Chaikin Oscillator. |
| obv          | Volume     |                          On-Balance Volume. |
| fib          | Custom     |                      Fibonacci Retracement. |
| multi        | Custom     | Plot multiple indicators on the same chart. |

:::note

Some functions will not be compatible with intraday data and some may be designed specifically for a daily window.  Interval labels on charts may still be described as "days" when the time series interval is intraday. Consult the help dialogue, by attaching `-h` to a command, for a reminder of the adjustable parameters.
:::

With some daily data now loaded, let's look at some charts!

## Examples

### Moving Averages

There are five types of moving averages available, they are grouped into the `Overlay` category.  It is possible to overlay multiple windows of time for each one, and it is also possible to overlay multiple versions of moving average.

#### Single MA Type

The help dialogue will explain the differences. For example, Zero-Lag Moving Average.

```console
zlma -h
```

```console
usage: zlma [-l N_LENGTH] [-o N_OFFSET] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]]

The zero lag exponential moving average (ZLEMA) indicator was created by John Ehlers and Ric Way. The idea is do a regular exponential moving average (EMA) calculation but
on a de-lagged data instead of doing it on the regular data. Data is de-lagged by removing the data from "lag" days ago thus removing (or attempting to) the cumulative
effect of the moving average.

options:
  -l N_LENGTH, --length N_LENGTH
                        Window lengths. Multiple values indicated as comma separated values. (default: [20])
  -o N_OFFSET, --offset N_OFFSET
                        offset (default: 0)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)

For more information and examples, use 'about zlma' to access the related guide.
```

For moving averages, there are two parameters: the window length and offset.  Let's examine the ZLMA at 50 and 200 days.

```console
zlma -l 50,200
```

![ZLMA 50,200](https://user-images.githubusercontent.com/85772166/233763992-157eb965-e5ca-48d6-b621-1e6596d4f784.png)

Drawing a chart with the Simple Moving Average shows the overlaps occur at different points in time.

```console
sma -l 50,200
```

![SMA 50,200](https://user-images.githubusercontent.com/85772166/233764006-45f6e6db-aa8c-4404-8997-68f96fbbe29e.png)

#### Multiple MA Types

Let's overlay the 200-day ZLMA with the 200-day SMA to see where they intersect.  This is accomplished using the `multi` function.

```console
multi -i sma[200],zlma[200]
```

:::note
Make note of the difference in parameters syntax.  With the `multi` function, parameters for each indicator must be surrounded with square brackets [ ].
:::

![SMA/ZLMA Overlay](https://user-images.githubusercontent.com/85772166/233764023-26991e03-6a82-47b6-9a6b-b2013dbdfffc.png)

Now let's see both 200 and 50-day moving averages.

```console
multi -i sma[50,200],zlma[50,200]
```

![SMA/ZLMA Overlay](https://user-images.githubusercontent.com/85772166/233764031-fd0375e9-f13f-43dd-b304-795168a0424b.png)

The last crossover point provides some confirmation of the current trend.  Intraday data might reveal more.  Let's see the one-hour MAs!

```console
load qqq -i 60/multi -i sma[50,200],zlma[50,200]
```

![SMA/ZLMA Hourly Overlay](https://user-images.githubusercontent.com/85772166/233764046-879252f8-3449-4f61-9098-6c538e130e47.png)

The ZLMA 50 has crossed over the SMA50, potentially signalling that the trend is near its exhaustion point.  Let's consult some other indicators using the hourly data now loaded.

### multi

Load multiple indicators on the same chart with the `multi` command.

```console
load qqq -i 60 -s 2023-01-01/multi rsi,vwap,atr
```

![multi rsi,vwap,atr](https://user-images.githubusercontent.com/85772166/233764057-46b82e00-0e93-4f69-a253-c74f102a5827.png)

The help dialogue for this function provides some guidance for setting the optional arguments for each indicator.

```console
multi -h
```

```console
usage: multi [-i INDICATORS] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]]

Plot multiple indicators on the same chart separated by a comma.

options:
  -i INDICATORS, --indicators INDICATORS
                        Indicators with optional arguments in the form of "macd[12,26,9],rsi,sma[20]" (default: None)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)

For more information and examples, use 'about multi' to access the related guide.
```

Making adjustments with this function requires knowing the parameters for each individual indicator.  They will have sensible default values but, where there are multiple parameters, it may not be obvious which order the numbers need to be entered.  Sometimes they are not even numbers, like MACD.

### macd

```console
macd --help

(🦋) /stocks/ta/ $ macd --help

usage: macd [--fast N_FAST] [--slow N_SLOW] [--signal N_SIGNAL] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]]

The Moving Average Convergence Divergence (MACD) is the difference between two Exponential Moving Averages. The Signal line is an Exponential Moving
Average of the MACD. The MACD signals trend changes and indicates the start of new trend direction. High values indicate overbought conditions, low
values indicate oversold conditions. Divergence with the price indicates an end to the current trend, especially if the MACD is at extreme high or low
values. When the MACD line crosses above the signal line a buy signal is generated. When the MACD crosses below the signal line a sell signal is
generated. To confirm the signal, the MACD should be above zero for a buy, and below zero for a sell.

options:
  --fast N_FAST         The short period. (default: 12)
  --slow N_SLOW         The long period. (default: 26)
  --signal N_SIGNAL     The signal period. (default: 9)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)

For more information and examples, use 'about macd' to access the related guide.
```

The one-hour MACD generated a downward signal trend two days ago.

```console
load qqq -i 60 -s 2023-01-01/macd
```

![MACD Hourly](https://user-images.githubusercontent.com/85772166/233764068-521b6218-2e4f-49d2-94b3-b4806b739a56.png)

:::note
Clicking and dragging the mouse near the corners at each axis allows the zooming to be locked to the X or Y axis only.
:::

### obv

Looking at the one-minute on-balance volume of QQQ today (April 21, 2023) reveals that massive volume spike occurred at 11:04.  The ceiling is now the floor.

```console
load qqq -i 1 -s 2023-04-21/macd
```

![On-Balance Volume](https://user-images.githubusercontent.com/85772166/233764081-ade1d33f-7524-41d0-9885-911a6270a11c.png)

The Accumulation/Distribution Line at the same one-minute interval signals in advance of the upward drift reversal, beginning to sell into the Friday close just before 14:00.

![Accumlation Distribution](https://user-images.githubusercontent.com/85772166/233764089-531dad18-d3c1-4bbb-aa6c-3c2c182f8fd3.png)

## Indicators Dashboard

This menu is also available as an experimental Dashboard Streamlit App.

```console
/dashboards/indicators
```

![Dashboards Menu](https://user-images.githubusercontent.com/85772166/233764105-85b944eb-6ff7-42c8-b2c7-f9cbdff51388.png)

![Indicators Dashboard](https://user-images.githubusercontent.com/85772166/233764115-7bfbbf8c-793e-4dbc-a8de-9f16007d68a9.png)
