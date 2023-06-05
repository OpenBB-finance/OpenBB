---
title: Stock Screener
keywords: [screen, screener, stock, stocks, historical, overview, valuation, financial, ownership, performance, technical, view, set, preset, presets, ini, scan, compare, tickers, metrics, how to, example, components, S&P, preset, signal name, description]
description: Learn the basics of the Stock Screener - a diverse tool for stock discovery.  Get to it from the `Stocks` menu by typing `scr` and then pressing `enter`.
---
The Stock Screener is a diverse tool for discovering comapanies.  It is a great jumping point for narrowing the universe of stocks at the beginning of a research workflow.  Get to the screener from the `Stocks` menu by typing `scr`, and then pressing `enter`.  There are six categories of statistics to sort the defined criteria by.

- Overview
- Valuation
- Financial
- Ownership
- Performance
- Technical

Running a screen is as easy as entering one of the choices above.

## How to use

The default preset upon entering the sub-menu is, `top_gainers`.  This preset, like some of the others, contain no parameters other than a signal - the name of the preset - and has no corresponding file which can be edited.  All signals are listed in the table below.  Use the commands `view` and `set` to select a new one.

| Preset and Signal Name |                                                                 Description |
| :--------------------- | --------------------------------------------------------------------------: |
| top_gainers            |                                  stocks with the highest % price gain today |
| top_losers             |                                  stocks with the highest % price loss today |
| new_high               |                                            stocks making 52-week high today |
| new_low                |                                             stocks making 52-week low today |
| most_volatile          |                 stocks with the highest widest high/low trading range today |
| most_active            |                                stocks with the highest trading volume today |
| unusual_volume         | stocks with unusually high volume today - the highest relative volume ratio |
| overbought             |                 stock is becoming overvalued and may experience a pullback. |
| oversold               |            oversold stocks may represent a buying opportunity for investors |
| downgrades             |                                         stocks downgraded by analysts today |
| upgrades               |                                           stocks upgraded by analysts today |
| earnings_before        |                      companies reporting earnings today, before market open |
| earnings_after         |                      companies reporting earnings today, after market close |
| recent_insider_buying  |                                  stocks with recent insider buying activity |
| recent_insider_selling |                                 stocks with recent insider selling activity |
| major_news             |                                 stocks with the highest news coverage today |
| horizontal_sr          | horizontal channel of price range between support and resistance trendlines |
| tl_resistance          |                                           once a rising trendline is broken |
| tl_support             |                                          once a falling trendline is broken |
| wedge_up               |         upward trendline support and upward trendline resistance (reversal) |
| wedge_down             |     downward trendline support and downward trendline resistance (reversal) |
| wedge                  |      upward trendline support, downward trendline resistance (contiunation) |
| triangle_ascending     |                upward trendline support and horizontal trendline resistance |
| triangle_descending    |              horizontal trendline support and downward trendline resistance |
| channel_up             |                         both support and resistance trendlines slope upward |
| channel_down           |                       both support and resistance trendlines slope downward |
| channel                |                       both support and resistance trendlines are horizontal |
| double_top             |             stock with 'M' shape that indicates a bearish reversal in trend |
| double_bottom          |             stock with 'W' shape that indicates a bullish reversal in trend |
| multiple_top           |                                       same as double_top hitting more highs |
| multiple_bottom        |                                     same as double_bottom hitting more lows |
| head_shoulders         |           chart formation that predicts a bullish-to-bearish trend reversal |
| head_shoulders_inverse |           chart formation that predicts a bearish-to-bullish trend reversal |

These signals offer a good starting point, and results can be narrowed by creating a custom preset with defined parameters.  Place new presets (which are text files saved as an `.ini` type) in the OpenBBUserData folder: `~/OpenBBUserData/presets/stocks/screener`.  Files saved here will populate as a choice the next time the Terminal is launched.   The next section provides guidance for using and creating presets.

:::note Refer to the template file [here](https://github.com/OpenBB-finance/OpenBBTerminal/files/11153280/all_parameters.txt) for all of the available parameters and accpeted values.

All of the included presets can be viewed online [here](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/miscellaneous/stocks/screener)
:::

Preset parameters are grouped into major categories:

- [General]
- [Descriptive]
- [Fundamental]
- [Technical]

The `General` category, for example, has two parameters: Order and Signal.  The accepted values for both are listed below.

```console
[General]
# Ticker, Company, Sector, Industry, Country, Market Cap., Price/Earnings, Forward Price/Earnings,
# PEG (Price/Earnings/Growth), Price/Sales, Price/Book, Price/Cash, Price/Free Cash Flow, Dividend Yield, Payout Ratio,
# EPS (ttm), EPS growth this year, EPS growth next year, EPS growth past 5 years, EPS growth next 5 years,
# Sales growth past 5 years, EPS growth qtr over qtr, Sales growth qtr over qtr, Shares Outstanding, Shares Float,
# Insider Ownership, Insider Transactions, Institutional Ownership, Institutional Transactions, Short Interest Share,
# Short Interest Ratio, Earnings Date, Return on Assets, Return on Equity, Return on Investment, Current Ratio,
# Quick Ratio, LT Debt/Equity, Total Debt/Equity, Gross Margin, Operating Margin, Net Profit Margin,
# Analyst Recommendation, Performance (Week), Performance (Month), Performance (Quarter), Performance (Half Year),
# Performance (Year), Performance (Year To Date), Beta, Average True Range, Volatility (Week), Volatility (Month),
# 20-Day SMA (Relative), 50-Day SMA (Relative), 200-Day SMA (Relative), 50-Day High (Relative), 50-Day Low (Relative),
# 52-Week High (Relative), 52-Week Low (Relative), Relative Strength Index (14), Average Volume (3 Month),
# Relative Volume, Change, Change from Open, Gap, Volume, Price, Target Price, IPO Date

Order = Ticker

# None (all stocks), Top Gainers, Top Losers, New High, New Low, Most Volatile, Most Active, Unusual Volume, Overbought,
# Oversold, Downgrades, Upgrades, Earnings Before, Earnings After, Recent Insider Buying, Recent Insider Selling, Major News,
# Horizontal S/R, TL Resistance, TL Support, Wedge Up, Wedge Down, Triangle Ascending, Triangle Descending, Wedge, Channel Up,
# Channel Down, Channel, Double Top, Double Bottom, Multiple Top, Multiple Bottom, Head & Shoulders, Head & Shoulders Inverse

Signal = Top Gainers

```

A new preset file should contain all four categories, even if no parameters are added.  The example below is a minimalist example of how it should be structured.  This preset is called, `djia_components`.

```console
# Author of preset: OpenBB
# Description: Filter for the Dow Jones Industrial Average components.

[General]

[Descriptive]

Index = DJIA

[Fundamental]

[Technical]
```

To set the preset to be the example above, use the `set` command and press the spacebar.  Use the up/down arrow keys to scroll through the presets.

```console
set djia_components
```

With a preset selected, select the type of data to return by entering one of the six commands listed at the top of this guide.  Each command returns a different set of columns which can be sorted by adding the optional `-s` argument, and selecting a choice populated by autocomplete.  The results will display as a table.

![Stocks Screener](https://user-images.githubusercontent.com/85772166/229921157-8297665a-1b88-4f4e-aeb1-91c1bb9aba7c.png)

## Examples

The examples below will demonstrate the expected outputs, and provide some context for getting started.

### View

See the specified parameters for a custom preset with the `view` function.

```console
view -p bull_runs_over_10pct
```

```console

 - General -
Order : Ticker
Signal: Top Gainers


 - Descriptive -


 - Fundamental -


 - Technical -
Performance: Today +10%
```

```console
view -p buffett_like
```

```console
 - General -


 - Descriptive -
Market Cap.   : +Mid (over $2bln)
Dividend Yield: Positive (>0%)


 - Fundamental -
EPS growthnext 5 years  : Positive (>0%)
Debt/Equity             : Under 0.5
Price/Free Cash Flow    : Under 50
Sales growthpast 5 years: Positive (>0%)
Return on Investment    : Over +15%
P/B                     : Under 3


 - Technical -

```

Some presets contain only a signal, therefore there are no parameters to view.  Any stock crossing the threshold for the signal will be returned.

```console
view -p channel_up
```

```console
This preset contains no parameters other than the signal.
```

### S&P 500 Sector Components

A series of presets are included that filter the S&P 500 constituents by sector.  There are no parameters, so these presets simply return the components for comparison.

![S&P 500](https://user-images.githubusercontent.com/85772166/229921343-605d0fbe-645f-4c69-83a9-a0034bc5c00e.png)

```console
/stocks/scr/set -p sp500_financial_sector/performance
```

Columns can also be sorted, filtered, or rearranged from within the tables.

![Screener Output](https://user-images.githubusercontent.com/85772166/229921470-ac5d9d9e-8489-45aa-9cc2-f0d8a156b172.png)

Changes made to an existing preset will be reflected immediately, restarting is only necessary when adding a new file.  The preset Financial Sector preset can be modified to filter only those companies with a Price-to-Book ratio of under 1.

```console

# Author of preset: OpenBB
# Description: Filter for the S&P 500 Financial Sector components.

[General]

[Descriptive]

Index = S&P 500
Sector = Financial

[Fundamental]

P/B = Under 1

[Technical]

```

Open presets in any simple text editor, add the desired parameters, save the file, then run the command again.  At the time of publication, twelve results were narrowed down from sixty-eight.  All available parameters and settings are listed in the text file [here](https://github.com/OpenBB-finance/OpenBBTerminal/files/11153280/all_parameters.txt).

![Financial Sector P/B Under 1](https://user-images.githubusercontent.com/85772166/229921644-ca14f08a-95f2-4ac3-8da3-49bbe4af3be4.png)

### CA

The tickers from the results of the last screen are stored in memory and can be taken into the [Comparison Analysis menu](https://docs.openbb.co/terminal/usage/intros/stocks/comparison) to undergo further scrutiny.

![Screener Results](https://user-images.githubusercontent.com/85772166/229921889-3ce97436-a768-4a74-b312-e6070459e2a9.png)

```console
set -p buffett_like
performance
?
ca
hcorr
```

![Correlation Matrix of Results](https://user-images.githubusercontent.com/85772166/229921977-fd31ff4c-d782-46fb-ba56-922cde5df8f0.png)
