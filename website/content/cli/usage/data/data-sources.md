---
title: Data sources
sidebar_position: 1
description: This page provides useful information on dealing with different data
  vendors when using the OpenBB Platform CLI. It outlines how to select a default data source,
  acquire API keys, and switch the data vendor using specific commands, all in an
  effort to streamline and improve the user's experience.
keywords:
- Terminal
- CLI
- data vendors
- API keys
- data sources
- FinancialModelingPrep
- Polygon
- AlphaVantage
- EODHD
- YahooFinance
- source
- stocks/fa/income
- changing data source
- Default data source
- /sources
- get --cmd
- set --cmd
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data sources - Data - Usage | OpenBB CLI Docs" />


## Selecting The Data Source In-Command

Many commands have multiple data sources associated with it. In order to specify the data vendor for that particular command, use the `--provider` argument.

Parameter choices can be viewed from the help dialogue, `-h` or `--help`.

```console
/equity/price/historical -h
```

```console
usage: historical --symbol SYMBOL [SYMBOL ...] [--interval INTERVAL] [--start_date START_DATE] [--end_date END_DATE] [--chart]
                  [--provider {fmp,intrinio,polygon,tiingo,yfinance}] [--start_time START_TIME] [--end_time END_TIME] [--timezone TIMEZONE]
                  [--source {realtime,delayed,nasdaq_basic}] [--sort {asc,desc}] [--limit LIMIT] [--extended_hours] [--include_actions]
                  [--adjustment {splits_and_dividends,unadjusted,splits_only}] [--adjusted] [--prepost] [-h] [--export EXPORT]
                  [--sheet-name SHEET_NAME [SHEET_NAME ...]]

Get historical price data for a given stock. This includes open, high, low, close, and volume.

options:
  --interval INTERVAL   Time interval of the data to return.
  --start_date START_DATE
                        Start date of the data, in YYYY-MM-DD format.
  --end_date END_DATE   End date of the data, in YYYY-MM-DD format.
  --chart               Whether to create a chart or not, by default False.
  --provider {fmp,intrinio,polygon,tiingo,yfinance}
                        The provider to use for the query, by default None.
                            If None, the provider specified in defaults is selected or 'fmp' if there is
                            no default.
  --extended_hours      Include Pre and Post market data. (provider: polygon, yfinance)
  --adjustment {splits_and_dividends,unadjusted,splits_only}
                        The adjustment factor to apply. Default is splits only. (provider: polygon, yfinance)
  -h, --help            show this help message
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files.

required arguments:
  --symbol SYMBOL [SYMBOL ...]
                        Symbol to get data for. Multiple comma separated items allowed for provider(s): fmp, polygon, tiingo, yfinance.

intrinio:
  --start_time START_TIME
                        Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'.
  --end_time END_TIME   Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'.
  --timezone TIMEZONE   Timezone of the data, in the IANA format (Continent/City).
  --source {realtime,delayed,nasdaq_basic}
                        The source of the data.

polygon:
  --sort {asc,desc}     Sort order of the data. This impacts the results in combination with the 'limit' parameter. The results are always returned in ascending order by date.
  --limit LIMIT         The number of data entries to return.

yfinance:
  --include_actions     Include dividends and stock splits in results.
```


### Setting The Default Source

The default data source for each command (where multiple sources are available) can be defined within the user configuration file: `/home/your-user/.openbb_platform/user_settings.json`.

Set the default data provider for the `/equity/price/historical` command by adding the following line to your `user_settings.json` file:

```json
{
  ...
  "defaults": {"routes": {"equity/price/historical": {"provider":"yfinance"}}}
  ...
}
```
