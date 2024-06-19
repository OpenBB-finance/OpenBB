---
title: Data Sources
sidebar_position: 7
description: This page explains how to select a provider for any specific command, and set a default source for a route.
keywords:
- Terminal
- CLI
- provider
- API keys
- FinancialModelingPrep
- Polygon
- AlphaVantage
- Intrinio
- YahooFinance
- source
- data
- default
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data Sources | OpenBB Platform CLI Docs" />

Many commands have multiple data sources associated with it. This page describes how to select from multiple providers.

:::important
API credentials are defined in the `user_settings.json` file.

Find all data providers [here](/platform/user_guides/extensions/), and manage all your credentials directly on the [OpenBB Hub](https://my.openbb.co/app/platform/credentials).
:::

## Data Source In-Command

To specify the data vendor for that particular command, use the `--provider` argument.

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
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png or jpg
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

:::note
Provider-specific parameters are listed at the bottom of the print out. They are ignored when entered, if it is not supported by the selected provider.
:::

## Setting The Default Source

The default data providers for each command can be defined within the user configuration file: `/home/your-user/.openbb_platform/user_settings.json`. You can set a single provider or a priority list. If a list is set, the command will use the first provider for which all required credentials set.

See the example below for `obb.equity.price.historical` command:

```json
# user_settings.json
{
    "defaults": {
        "commands": {
            "equity.price.historical": {
                "provider": "fmp"
            },
            "equity.fundamental.balance": {
                "provider": ["intrinio", "fmp", "polygon"]
            },
            ...
        }
    }
}
```
