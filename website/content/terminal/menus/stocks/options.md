---
title: Options
description:
  This is an informative page providing a detailed overview of how to navigate
  and use the Options Menu to analyze equity options. It discusses the functions,
  and gives clear examples of how to fetch and analyze options data such as chains,
  Greeks, expiration dates, and put/call ratios using different financial data sources.
keywords:
  - equity options
  - options menu
  - financial instruments
  - derivatives
  - due diligence
  - YahooFinance
  - Nasdaq
  - Tradier
  - Intrinio
  - options data
  - options chains
  - options functions
  - ticker symbol
  - unusual options
  - fdscanner.com
  - option chain
  - put/call ratio
  - expiration date
  - volatility smile
  - second order Greeks
  - greeks command
  - puts
  - calls
  - surface
  - spx
  - ndx
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Options - Stocks - Menus | OpenBB Terminal Docs" />

The Options menu provides the user with tools for analyzing equity options. Wikipedia is a great resource for definitions and for learning about the mechanics of derivatives, read it [here](<https://en.wikipedia.org/wiki/Option_(finance)>). These are complex, leveraged, financial instruments requiring specialized knowledge and a different frame-of-mind than the approach taken by an equities long-only investor. Always conduct thorough due diligence.

## Usage

Navigate to the menu by typing `options`, from the `/stocks` menu, and then pressing enter. The menu can also be entered by the absolute path:

```console
/stocks/options
```

The source for the options data can be defined using the `load` command, and a default preference is be defined in the `/sources` menu - or on the [OpenBB Hub](https://my.openbb.co). The chains data returned will vary by source. The following sources are currently available to use:

- YahooFinance
- Nasdaq
- Tradier (requires API key)
- Intrinio (requires API key)

The menu can be entered without a ticker symbol loaded. If one is already loaded from the stocks menu, it will automatically fetch the chains data from the default source. The commands displayed above the currently active Ticker and Expiry do not require any data to be loaded, while the functions below do.

| Function Key |                                                                       Description |
| :----------- | --------------------------------------------------------------------------------: |
| calc         |                                  A basic payoff diagram for a single call or put. |
| chains       |                                                Display options chains and Greeks. |
| eodchain     |                           Gets the option chain for a ticker, on a specific date. |
| exp          |                                                  Select a target expiration date. |
| greeks       |                          Shows or recalculates the Greeks for an expiration date. |
| grhist       |                             Plot the historical Greeks of an individual contract. |
| hedge        |                        A calculator for weighting a position to neutralize delta. |
| hist         |                                      Historical prices of an individual contract. |
| info         |                                                Basic stats for the options chain. |
| load         |                                                                Load a new ticker. |
| oi           |                                                           Plot the open interest. |
| plot         |                                              Plot x vs. y as defined by the user. |
| pcr          | Display historical rolling put/call ratios for a ticker over a selectable window. |
| screen       |                                                              An options screener. |
| unu          |                                      Unusual options activity for S&P 500 stocks. |
| voi          |                                       Plot the volume and open interest together. |
| vol          |                                                                  Plot the volume. |
| vsurf        |                                                     3-D volatility surface chart. |

The examples here will start by entering the Options menu without a ticker symbol loaded.

```console
/stocks/options
```

### UNU

Unusual options are described as those having a very high volume/open interest ratio. This function is built using the data provided by [fdscanner.com](https://fdscanner.com). By default, the top 20 options with the highest vol/OI ratio are returned as a table.

```console
unu
```

With the new interactive tables, it may be better to remove the limit and utilize the table's built-in filtering.

```console
unu -l 500
```

This returned over 500 results which can then be filtered, for example, by June/23 expirations. There were thirty-four results.

![Unusual Options](https://user-images.githubusercontent.com/85772166/234757578-da79b032-416b-4e0a-b759-a05f651f28a2.png)

### Load

Let's take a look at one of these tickers, GM. The default source will be `YahooFinance`. Select a different source by attaching `--source` to the command.

```console
load gm
```

:::note
**This obtains the data for all the expirations, very long chains - like SPY - may take a few moments to load.**
:::

```console
Getting Option Chain ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
Loaded option chain from YahooFinance
```

### PCR

The `pcr` command plots a rolling put/call ratio (ten years max) over a selectable window of time (default is 30 days).

```console
pcr -l 90 -s 2010-04-01
```

![GM 90-Day P/C Ratio](https://user-images.githubusercontent.com/85772166/234757627-8250700b-1586-4535-948e-33d6ff18c4a2.png)

Adding in an overlay from an exported CSV file adds more context to the story.

```console
/stocks/load GM --start 2013-04-01 --monthly --export gm_monthly.csv
```

![GM 90-Day P/C Ratio Against Share Price](https://user-images.githubusercontent.com/85772166/234757705-0bc63a89-0cb8-4d32-a403-2a8aa7b0337a.png)

### EXP

After loading, select an expiration date for the chain using the `exp` command. To display the list of available expirations, use the function with no arguments. The date can be selected by entering a number - with `0` being the nearest expiry - or by entering the date, formatted as `YYYY-MM-DD`.

```console
exp 2023-06-02
```

```console
Expiration set to 2023-06-02
```

### Plot

Use the `plot` function to draw the volatility smile for the selected expiration date.

```console
plot -c smile
```

![Volatility Smile](https://user-images.githubusercontent.com/85772166/234757758-537ada39-cf47-49e3-a861-b97c4b7a9919.png)

### Greeks

Calculate the second order Greeks - Rho, Phi, Charm, Vanna, Vomma - with the `greeks` command.

```console
greeks --risk-free 4.8 --all
```

![Greeks Command](https://user-images.githubusercontent.com/85772166/234757813-c6a7b04f-3a20-4c7b-841b-1cd3fec7c088.png)

![Second Order Greeks](https://user-images.githubusercontent.com/85772166/234757864-749ff78e-00c3-465a-b1b1-f4d0d2991c84.png)
