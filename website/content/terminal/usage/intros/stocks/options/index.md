---
title: Options
keywords: [Options, stocks, derivatives, puts, calls, oi, vol, greeks, voi, volatility, vsurf, chains, parity, binom, screen, pricing, hedge, pcr, info, hist, grhist, plot, parity, how to, example, navigation]
excerpt: This guide introduces the Options sub-menu, within the Stocks menu, and provides examples for use.
---
## Overview

The Options menu provides the user with tools for analyzing equity options.  Wikipedia is a great resource for definitions and for learning about the mechanics of derivatives, read it [here](https://en.wikipedia.org/wiki/Option_(finance)).  These are complex, leveraged, financial instruments requiring specialized knoweledge and a different frame-of-mind than the approach taken by an equities long-only investor.  Always conduct thorough due diligence.

### The Options Menu

Navigate to the menu by typing `options`, from the `Stocks` menu, and then pressing enter. Alternatively, absolute path navigation can jump straight there, from anywhere. `/stocks/options`.  The source for the options data can be defined using the `load` command, or a default preference can be defined using the `/sources` menu.  The chains data returned will vary by source.  The following sources are currently available to use:

- YahooFinance
- Nasdaq
- Tradier (requires API key)
- Intrinio (requires API key)

The menu can be entered without a ticker symbol loaded.  If one is already loaded from the stocks menu, it will automatically fetch the chains data from the default source.    The commands displayed above the currently active Ticker and Expiry do not require any data to be loaded, while the functions below do.

| Function Key | Description |
| :----------- | ----------: |
|calc |A basic payoff diagram for a single call or put. |
|chains |Display options chains and Greeks. |
|eodchain |Gets the option chain for a ticker, on a specific date. |
|exp |Select a target expiration date. |
|greeks |Shows or recalculates the Greeks for an expiration date. |
|grhist |Plot the historical Greeks of an individual contract. |
|hedge |A calculator for weighting a position to neutralize delta. |
|hist |Historical prices of an individual contract. |
|info |Basic stats for the options chain. |
|load |Load a new ticker. |
|oi |Plot the open interest. |
|plot |Plot x vs. y as defined by the user. |
|pcr |Display historical rolling put/call ratios for a ticker over a selectable window. |
|screen |An options screener. |
|unu |Unusual options activity for S&P 500 stocks. |
|voi |Plot the volume and open interest together. |
|vol |Plot the volume. |
|vsurf |3-D volatility surface chart. |

### Examples

The examples here will start by entering the Options menu without a ticker symbol loaded.

```console
/stocks/options
```

#### unu

Unusual options are described as those having a very high volume/open interest ratio.  This function is built using the data provided by [fdscanner.com](https://fdscanner.com).  By default, the top 20 options with the highest vol/OI ratio are returned as a table.

```console
unu
```

Ticker   | Exp        |   Strike | Type   |   Vol/OI |   Vol |   OI |   Bid |   Ask |
|:---------|:-----------|---------:|:-------|---------:|------:|-----:|------:|------:|
| TFC      | 2023-05-19 |     34   | Call   |    127.2 | 15904 |  125 |  0.4  |  0.5  |
| SCHW     | 2023-06-02 |     40   | Put    |     55.5 | 11996 |  216 |  0.28 |  0.34 |
| TSLA     | 2023-05-05 |    149   | Put    |     49.3 | 57454 | 1165 |  2.93 |  2.95 |
| TSLA     | 2023-04-28 |    157.5 | Call   |     46.8 | 99677 | 2132 |  1.39 |  1.4  |
| USB      | 2023-05-19 |     32   | Call   |     44.9 |  6692 |  149 |  1.35 |  1.4  |
| NOC      | 2023-05-19 |    440   | Put    |     43.8 |  4420 |  101 |  6    |  7.2  |
| GM       | 2023-06-02 |     28   | Put    |     43.1 |  5867 |  136 |  0.32 |  0.35 |
| AAPL     | 2023-05-19 |    167.5 | Call   |     41.6 | 10888 |  262 |  2.91 |  2.93 |
| ATVI     | 2023-07-21 |     85   | Call   |     36.5 |  5772 |  158 |  1.59 |  1.71 |
| TSLA     | 2023-04-28 |    155   | Call   |     35.2 | 76831 | 2182 |  2.42 |  2.44 |
| FRC      | 2023-04-28 |      6   | Call   |     33.3 |  9024 |  271 |  0.65 |  0.75 |
| JPM      | 2023-11-17 |    105   | Put    |     33.1 |  5797 |  175 |  2.47 |  2.52 |
| MSFT     | 2023-05-05 |    295   | Put    |     30.8 |  8676 |  282 |  4.2  |  4.3  |
| MSFT     | 2023-04-28 |    295   | Put    |     29.6 | 40431 | 1366 |  2.12 |  2.15 |
| FRC      | 2023-04-28 |      7   | Call   |     29.1 | 10569 |  363 |  0.3  |  0.4  |
| AAL      | 2023-11-17 |     16   | Call   |     26.6 |  4556 |  171 |  0.65 |  0.66 |
| MSFT     | 2023-07-21 |    295   | Put    |     26.4 | 12707 |  482 | 12.55 | 12.65 |
| FRC      | 2023-05-05 |      1.5 | Put    |     26.1 | 49299 | 1889 |  0.2  |  0.3  |
| HPQ      | 2023-05-05 |     29.5 | Call   |     25.7 |  3986 |  155 |  0.28 |  0.31 |
| MSFT     | 2023-04-28 |    292.5 | Put    |     20.8 | 24519 | 1178 |  1.28 |  1.3  |

With the new interactive tables, it may be better to remove the limit and utilize the table's built-in filtering.

```console
unu -l 500
```

This returned over 500 results which can then be filtered, for example, by June/23 expirations.  There were thirty-four results.

![Unusual Options](https://user-images.githubusercontent.com/85772166/234757578-da79b032-416b-4e0a-b759-a05f651f28a2.png)

#### load

Let's take a look at one of these tickers, GM.  The default source will be `YahooFinance`.  Select a different source by attaching `--source` to the command.

```console
load gm
```

```console
Getting Option Chain ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
Loaded option chain from YahooFinance
```

#### pcr

The `pcr` command plots a rolling put/call ratio (ten years max) over a selectable window of time (default is 30).

```console
pcr -l 90 -s 2010-04-01
```

![GM 90-Day P/C Ratio](https://user-images.githubusercontent.com/85772166/234757627-8250700b-1586-4535-948e-33d6ff18c4a2.png)

Adding in an overlay from an exported CSV file adds more context to the story.

```console
/stocks/load GM --start 2013-04-01 --monthly --export gm_monthly.csv
```

![GM 90-Day P/C Ratio Against Share Price](https://user-images.githubusercontent.com/85772166/234757705-0bc63a89-0cb8-4d32-a403-2a8aa7b0337a.png)

#### exp

After loading, select an expiration date for the chain using the `exp` command.  To display the list of available expirations, use the function with no arguments.  The date can be selected by entering a number - with `0` being the nearest expiry - or by entering the date, formatted as `YYYY-MM-DD`.

```console
exp 2023-06-02
```

```console
Expiration set to 2023-06-02
```

#### plot

Use the `plot` function to draw the volatility smile for the selected expiration date.

```console
plot -c smile
```

![Volatility Smile](https://user-images.githubusercontent.com/85772166/234757758-537ada39-cf47-49e3-a861-b97c4b7a9919.png)

#### greeks

Calculate the second order Greeks - Rho, Phi, Charm, Vanna, Vomma - with the `greeks` command.

```console
greeks --risk-free 4.8 --all
```

![Greeks Command](https://user-images.githubusercontent.com/85772166/234757813-c6a7b04f-3a20-4c7b-841b-1cd3fec7c088.png)

![Second Order Greeks](https://user-images.githubusercontent.com/85772166/234757864-749ff78e-00c3-465a-b1b1-f4d0d2991c84.png)
