---
title: Technical Analysis
keywords:
  [
    "technical",
    "analysis",
    "ta",
    "t/a",
    "intraday",
    "daily",
    "indicators",
    "signals",
    "average",
    "moving",
    "exponential",
    "rsi",
    "fibonacci",
    "retracement",
    "bollinger",
    "heltner",
    "accumulation",
    "distribution",
    "obv",
    "on-balance",
    "volume",
    "volatility",
    "trend",
    "momentum",
    "overlap",
    "crypto",
    "stocks",
    "funds",
    "etf",
    "etfs",
  ]
date: "2022-06-17"
type: guides
status: publish
excerpt: "This guide introduces the Technical Analysis menu, which is common across many sections of the OpenBB Terminal."
---

The Technical Analysis menu offers the user a suite of tools for analyzing the technical components of an asset's trading history. The menu can be found in most wings of the Terminal:

- <a href="/terminal/guides/intros/crypto/" target="_blank" rel="noreferrer noopener">Crypto</a>
- <a href="/terminal/guides/intros/stocks/" target="_blank" rel="noreferrer noopener">Stocks</a>
- <a href="/terminal/guides/intros/etf/" target="_blank" rel="noreferrer noopener">ETF</a>
- <a href="/terminal/guides/intros/forex/" target="blank">Forex</a>

The commands are divided by categories that define their purpose for general-use:

- Overlap - Moving averages
- Momentum - Oscillating signals
- Trend - Directional strength
- Volatility - Width of the price bands
- Volume - Singling out volume
- Custom - Fibonacci retracements

All commands in this menu will rely on the interval and window chosen when <a href="/terminal/reference/stocks/load" target="_blank" rel="noreferrer noopener">loading an asset for analysis</a>. Refer to the directory tree on the left side of the page for information on individual commands. To get a better understanding of what these features are, and the formulas behind them, a number of sources should be consulted; but, a good starting point is <a href="https://www.investopedia.com/terms/t/technicalanalysis.asp" target="_blank" rel="noreferrer noopener">Investopedia</a>.

### How to use

To begin, enter the menu from one of the menus listed above by entering `ta`.

![The Technical Analysis menu, with BTC loaded](https://user-images.githubusercontent.com/85772166/174499113-02648936-f8d1-40ca-8ba3-036fb4324666.png)

Choose a beginning and end date to see a volume-weighted average price chart of the loaded ticker. `vwap --start 2022-01-01 --end 2022-06-17`

![BTC VWAP YTD](https://user-images.githubusercontent.com/85772166/174499127-cc20f16c-dd68-4ce3-9d10-cd6ce762a346.png)

The Fibonacci retracements are drawn with <a href="https://en.wikipedia.org/wiki/Fibonacci_number" target="_blank" rel="noreferrer noopener">`fib`</a>

![SPY Fibonacci retracement from the recent lower high](https://user-images.githubusercontent.com/85772166/174499173-5d3dbdb7-8147-459b-88d3-7caae9102aa5.png)

See the <a href="https://www.investopedia.com/terms/o/onbalancevolume.asp" target="_blank" rel="noreferrer noopener">on-balance volume</a> for the time-period loaded.

![OBV for ARKK YTD](https://user-images.githubusercontent.com/85772166/174499183-42d246d9-0a0f-4c76-8c4e-de22ad2e396d.png)

The help dialogue for any feature is printed by attaching `-h` to the command.

### Examples

`recom` & `summary` are commands available only with a stock loaded as the asset. `summary` is a text description of the technical conditions.

```
(🦋) /stocks/ta/ $ summary
MSFT price has changed 1.29% in the last 3 days and 1.09% yesterday.
RSI is less than 30 and the indicator is pointing downwards.
Asset is in the oversold area.
MACD is in the Bearish area and the histogram is moving upwards.
MSFT price is trading below the 200-day SMA line and the SMA is trending down.
The asset price is between the Middle and the Lower Bollinger Bands.
```

`recom` projects buy & sell signals for the short-term.

![Recommendations from T/A](https://user-images.githubusercontent.com/85772166/174499195-9d4f8604-dec9-453f-815d-6c89f2b8b216.png)

Bollinger Bands with a 1-minute resolution for AMZN - `bbands`

![AMZN Bollinger Bands](https://user-images.githubusercontent.com/85772166/174499209-ec7eb606-bc86-4cb3-8375-a24b2c235085.png)
![AMZN Bollinger Bands](https://user-images.githubusercontent.com/85772166/174499232-63412ad9-e74c-4f44-a0f3-8722d98a27c6.png)

The Accumulation/Distribution line of AMZN - `ad`

![AMZN Accumulation/Distribution Line](https://user-images.githubusercontent.com/85772166/174499247-e63f8f57-a06a-446b-bca3-0fe89258fd4b.png)

To play a demonstration of this menu in the OpenBB Terminal run,
`exe ta_demo.openbb`, from the main menu.
