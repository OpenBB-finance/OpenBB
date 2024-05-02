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

<HeadTitle title="Data sources - Data - Usage | OpenBB Platform CLI Docs" />

import TutorialVideo from '@site/src/components/General/TutorialVideo.tsx';

<TutorialVideo
  youtubeLink="https://www.youtube.com/embed/cvSwG96Yf4o?si=oswcJYUH51F206Hu"
  videoLegend="Short video on where the data comes from"
/>

:::note
Note that the commands and menus may vary.
:::

## Relationship With Data Vendors

Most commands will require obtaining API keys from various data providers. OpenBB provides methods for consuming these data feeds, but has no control over the quality or quantity of data provided to an end-user. **No API Keys are required to get started using the CLI**.

See the list of providers [here](https://my.openbb.co/app/platform/data-providers).

:::note
OpenBB doesn't store any financial data in its servers. We aggregate access to multiple data sources through API calls and standardize that interaction to provide users a seamless experience when dealing with different data vendors
:::

## Changing the Data Source In-Command

Many commands have multiple data sources associated with it. A great example is `/equity/price/historical`.. In order to specify the data vendor for that particular command, use the `--provider` argument.

This also becomes clear from the help menu.

```console
/equity/price/historical -h
```

```console
usage: historical --symbol SYMBOL [SYMBOL ...] [--interval INTERVAL] [--start_date START_DATE] [--end_date END_DATE] [--chart]
                  [--provider {alpha_vantage,cboe,fmp,intrinio,polygon,tiingo,tmx,tradier,yfinance}] [--adjustment {splits_only,splits_and_dividends,unadjusted}] [--extended_hours]
                  [--adjusted] [--use_cache] [--start_time START_TIME] [--end_time END_TIME] [--timezone TIMEZONE] [--source {realtime,delayed,nasdaq_basic}] [--sort {asc,desc}]
                  [--limit LIMIT] [--include_actions] [--prepost] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]]

Get historical price data for a given stock. This includes open, high, low, close, and volume.

optional arguments:
  --interval INTERVAL   Time interval of the data to return.
  --start_date START_DATE
                        Start date of the data, in YYYY-MM-DD format.
  --end_date END_DATE   End date of the data, in YYYY-MM-DD format.
  --chart               Whether to create a chart or not, by default False.
  --provider {alpha_vantage,cboe,fmp,intrinio,polygon,tiingo,tmx,tradier,yfinance}
                        The provider to use for the query, by default None.
                            If None, the provider specified in defaults is selected or 'alpha_vantage' if there is
                            no default.
  -h, --help            show this help message
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files.

required arguments:
  --symbol SYMBOL [SYMBOL ...]
                        Symbol to get data for. Multiple comma separated items allowed for provider(s): alpha_vantage, cboe, fmp, polygon, tiingo, tmx, tradier, yfinance.

alpha_vantage:
  --adjustment {splits_only,splits_and_dividends,unadjusted}
                        The adjustment factor to apply. 'splits_only' is not supported for intraday data.
  --extended_hours      Include Pre and Post market data.
  --adjusted            This field is deprecated (4.1.5) and will be removed in a future version. Use 'adjustment' set as 'splits_and_dividends' instead.

cboe:
  --use_cache           When True, the company directories will be cached for 24 hours and are used to validate symbols. The results of the function are not cached. Set as False to bypass.

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
  --prepost             This field is deprecated (4.1.5) and will be removed in a future version. Use 'extended_hours' as True instead.

For more information and examples, use 'about historical' to access the related guide.

```

:::info
Each provider also brings the possibility of different arguments. For example, the `polygon` provider has the `--sort` and `--limit` arguments, while the `yfinance` provider has the `--include_actions` and `--prepost` arguments.
:::

The available providers for each command are displayed on the right of the command, and they can be distinguished by the square brackets and distinct font color group. By default, if the user doesn't specify `--provider` the CLI will use the first data provider displayed.

### Setting Default Sources

The default data source for each command (where multiple sources are available) can be defined within the user configuration file: `/home/your-user/.openbb_platform/user_settings.json`.

For example, changing the default data provider for the `/equity/price/historical` command would be adding the following line to the user configuration file:

```json
{
  ...
  "defaults": {"routes": {"equity/price/historical": {"provider":"yfinance"}}}
  ...
}
```
