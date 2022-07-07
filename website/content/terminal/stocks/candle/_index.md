---
title: The Candle Command
keywords: "charts, , chart, candle, candles, price, OHLC, OHLC+V, open, low, high, close, volume, date, interval, intervals, candlestick, raw, csv, export, json, xlsx"
date: "2022-07-01"
type: guides
status: publish
excerpt: "This guide introduces the candle command, and provides examples of different uses."
geekdocCollapseSection: true
---

The origin of candlestick charts is attributed to 18th Century rice traders from Japan, and is thought to have gained popularity in the late 1800s. Read the <a href="https://en.wikipedia.org/wiki/Candlestick_chart" target="_blank">Wiki</a> to learn more. This guide is intended to introduce the `candle` command, and gives examples for more advanced use-cases. It is a one of the most important commands in the OpenBB Terminal, allowing the user to accomplish several tasks:
  - Chart OHLC+V for the time-series requested by the `load` command.
  - Display tables of raw data, and sort columns.
  - Export the dataframe of the `load` function as a CSV, XLSX, or JSON file.
  - Add user-defined moving averages to the chart.

````
usage: candle [-p] [--sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}] [-d] [--raw] [-t] [--ma MOV_AVG] [-h] [--export EXPORT] [-l LIMIT]

Shows historic data for a stock

optional arguments:
  -p, --plotly          Flag to show interactive plotly chart (default: True)
  --sort {AdjClose,Open,Close,High,Low,Volume,Returns,LogRet}
                        Choose a column to sort by (default: )
  -d, --descending      Sort selected column descending (default: True)
  --raw                 Shows raw data instead of chart (default: False)
  -t, --trend           Flag to add high and low trends to candle (default: False)
  --ma MOV_AVG          Add moving average in number of days to plot and separate by a comma (default: None)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 20)
````

<h2>How to use the Candle Command</h2>

While this guide focuses on `Stocks`, the candle command is not only found in this menu; and elsewhere, the functions remain consistent. Entering the command plainly, as `candle`, will display the time-series as loaded.

<img width="1162" alt="Loading the ticker TLT and entering `candle`" src="https://user-images.githubusercontent.com/85772166/177718644-4917c402-16b8-4478-9557-e4f0a3531957.png">

![Default candlestick chart, with the default load settings](https://user-images.githubusercontent.com/85772166/177719305-2f786262-cecb-495a-a8ef-1e7693ad37d7.png)

At the bottom of the chart are some controls for the view. Select the button with four arrows, then hold the left or right mouse button while dragging, to pan and zoom.

<img width="326" alt="Zooming in" src="https://user-images.githubusercontent.com/85772166/177719635-58a62a3f-4d8c-4567-9ebd-0abe5c73abb8.png">

<img width="1417" alt="Zooming in" src="https://user-images.githubusercontent.com/85772166/177719705-946f6c70-f40c-40dd-8182-1d840a3bd4ac.png">

The look and feel of the charts can be altered with style sheets, located in the `styles` folder of the local OpenBB installation path. Styles placed in the `user` folder are given preference over the `default` settings. Nearly every detail of the chart can be customized, subtle differences can make a big impact. To learn more about these style sheets, consult the <a href="https://matplotlib.org/stable/api/rcsetup_api.html#module-matplotlib.rcsetup" target="blank">Matplotlib documentation</a>.

Trend lines are drawn by attaching the optional argument, `-t`.

`candle -t`

![Trend lines added](https://user-images.githubusercontent.com/85772166/177720194-7cca22b9-2d72-45a4-bfc5-c98d9943dbe2.png)

User-defined moving averages are drawn by adding the flag, `--ma`, followed by a comma-separated list of values. `candle -t --ma 50,150,200`

![Adding moving averages to the cartoon](https://user-images.githubusercontent.com/85772166/177720107-f9514f3b-5850-4101-90f9-a9b7617c1587.png)

<h2>Examples</h2>

Showing a weekly or monthly chart is accomplished by loading the ticker with the `-w` or `-m` flags. A simple way to call the entire history is to establish a start date of 1900-01-01. Staying with the example ticker from above, this would look like: `load tlt -s 1900-01-01 -m`

<img width="1258" alt="Loading complete $TLT history, with monthly candles" src="https://user-images.githubusercontent.com/85772166/177720296-7a3d3743-138d-448b-9b9b-76c54dc281cc.png">

Viewing the monthly candles will provide a different perspective, and make a cleaner long chart.

![Monthly TLT candles from inception](https://user-images.githubusercontent.com/85772166/177720477-c5554bec-bdcc-40b0-b498-8533eea0c2bb.png)

Keep in mind that the moving average flag will respond to the loaded interval. A period of 1 is now one month; adjust the flags accordingly. `candle --ma 2,6,18`

![3, 6, 18 month moving averages](https://user-images.githubusercontent.com/85772166/177720665-25b7c5b2-fbcf-477d-bf3f-6f335288a3ea.png)

As weekly candles, the data can be further scrutinized.

````
(🦋) /stocks/ $ load TLT -s 2002-08-01 -w

Loading Daily TLT stock with starting period 2002-07-29 for analysis.
````
![Weekly TLT candles](https://user-images.githubusercontent.com/85772166/177720756-57dfb4d5-1f8a-4e32-8d4b-fb712ab1f944.png)

To chart the intraday movements, the interval is selected by raising the flag, `-i`, and adding the numeric interval in minutes. The maximum available history is loaded unless otherwise expressed with a starting date, `-s`. 

````
(🦋) /stocks/ $ load tlt -i 15

Loading Intraday 15min TLT stock with starting period 2022-05-08 for analysis.

Datetime: 2022 Jul 06 18:39
Timezone: America/New_York
Currency: USD
Market:   OPEN
Company:  iShares 20+ Year Treasury Bond 

(🦋) /stocks/ $ candle
````
![TLT fifteen-minute candles](https://user-images.githubusercontent.com/85772166/177720969-8910ca62-c794-4c06-9bd7-0b08fc99127a.png)

Switching back to the daily chart, the `--raw` flag can be used to quickly reference highs and lows. Including a limit for the number of results, `-l`, is useful to only show high and low, with `-d` attached to sort by descending values.

````
(🦋) /stocks/ $ load tlt -s 2002-07-30

(🦋) /stocks/ $ candle -h

(🦋) /stocks/ $ candle --sort Volume -d --raw -l 5
````

The top five days of trading volume:

<img width="1387" alt="Raw output, sorting by volume" src="https://user-images.githubusercontent.com/85772166/177721104-77d424c4-b6b7-45fc-a824-5f29c563379d.png">

If that same stock is loaded using an alternate source of data, there might be new information available now. `(🦋) /stocks/ $ load tlt -s 2002-07-30 --source polygon`

<img width="1385" alt="Raw candle data from Polygon" src="https://user-images.githubusercontent.com/85772166/177721200-8c3eeb30-485c-4c9c-af53-21c53c7c6ac5.png">

There are notable differences between this raw data and the raw data requested from the default source:
  - There is an additional column for volume-weighted price
  - There is an additional column for the number of transactions per interval.
  - While the highest volume days are the same, the actual values are different.
  - The historical daily data from a source does not always cover the entire trading history.

While the differences may be small, they are extremely important to be aware of. It is not that one is *wrong*, but that the other is *more inclusive*. How many exchanges and trading venues does the consolidated feed cover? Three markets? Five? All of them? How is the data curated, compiled, and verified? Does that even matter? These are personal choices and considerations, not limited to OpenBB, investors face on a daily basis. The OpenBB Terminal is a tool for any investor to make better, more informed, decisions.

Finally, the export function allows the user to export the currently loaded dataframe as a CSV, JSON, or XLSX file. These files can be used elsewhere in the terminal as inputs for other functions.

````
(🦋) /stocks/ $ candle --raw --export xlsx
Saved file: /Users/danglewood/desktop/exports/20220706_222437_stocks_raw_data_TLT.xlsx
````

Back to <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/stocks/" target="_blank">Introduction to the Stocks Menu</a>
