---
sidebar_position: 2
title: Changing Sources
description: How to change which data sources are the default source for commands run in the OpenBB Terminal.
keywords: [source, sources, default source, datasources, api keys, api, keys, openbb sdk, yfinance, yahoo finance, alphavantage polygon, EODHD, change the source]

---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Changing Sources - Terminal | OpenBB Docs" />

Many commands have multiple datasources attached to it. A great example is `/stocka/fa/income` that allows you to select FinancialModelingPrep, Polygon, AlphaVantage, EODHD or YahooFinance. Many have a default source, but you can change the default sources of each command via two methods.

## Changing the Source

Returning to the example of the `income` command instead the `stocks/fa` menu. This source has multiple sources to choose from. You are able to specify this source with the `--source` argument. This also becomes clear from the help menu.

```
(🦋) /stocks/fa/ $ income -h

usage: income [-t TICKER] [-q] [-r] [-p column] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]] [-l LIMIT] [--source {FinancialModelingPrep,Polygon,AlphaVantage,EODHD,YahooFinance}]

Prints a complete income statement over time. This can be either quarterly or annually.

optional arguments:
  -t TICKER, --ticker TICKER
                        Ticker to analyze (default: None)
  -q, --quarter         Quarter fundamental data flag. (default: False)
  -r, --ratios          Shows percentage change of values. (default: False)
  -p column, --plot column
                        Rows to plot, comma separated. (-1 represents invalid data) (default: None)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 5)
  --source {FinancialModelingPrep,Polygon,AlphaVantage,EODHD,YahooFinance}
                        Data source to select from (default: FinancialModelingPrep)

For more information and examples, use 'about income' to access the related guide.
```

Within the source arguments it shows the exact sources as previously mentioned. Therefore, with this information in hand it is possible to switch to a different source e.g. with `income --source Polygon`. Do keep in mind that you might need to have an API key to use this source, see [here](/terminal/basics/advanced/api-keys).

## Working with the Sources Menu

In case you are looking to change the default source al together, you can do so via the sources menu as found on the homepage of the OpenBB Terminal.

```
(🦋) / $ sources

╭─────────────────────────────────────────────────────────────────────────────────────────────────── Data Sources ───────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                                                                                                                    │
│ Get and set default data sources:                                                                                                                                                                                  │
│     get                get available data sources associated with command                                                                                                                                          │
│     set                set default data source for a command                                                                                                                                                       │
│                                                                                                                                                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── OpenBB Terminal (https://openbb.co) ─╯
```

For example, if you would like to change the default data provider from the `income` command from the `stocks/fa` menu you can first run the command `get --cmd stocks/fa/income`. This returns the following:

```
(🦋) /sources/ $ get --cmd stocks/fa/income

Default   : FinancialModelingPrep
Available : FinancialModelingPrep, Polygon, AlphaVantage, EODHD, YahooFinance
```

Then, with `set` you can change the default data provider. For example, we can change the data provider to `Polygon` with
the following:

```
(🦋) /sources/ $ set --cmd stocks/fa/income --source Polygon

Default data source for 'stocks/fa/income' set to 'Polygon'.

(🦋) /sources/ $ get --cmd stocks/fa/income

Default   : Polygon
Available : Polygon, FinancialModelingPrep, AlphaVantage, EODHD, YahooFinance
```
