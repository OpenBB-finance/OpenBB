---
title: historical
description: Learn how to use the `obb.equity.price.historical` function to load historical
  price data for a specific stock ticker. Find out about the available parameters
  and providers, as well as the structure of the returned data and the columns it
  contains.
keywords: 
- equity historical price
- load stock data
- specific ticker
- python function
- equity data parameters
- alpha vantage provider
- fmp provider
- intrinio provider
- polygon provider
- yfinance provider
- equity historical data returns
- equity data columns
- alpha vantage data columns
- cboe data columns
- fmp data columns
- intrinio data columns
- polygon data columns
- yfinance data columns
---

<!-- markdownlint-disable MD041 -->

Equity Historical price. Load stock data for a specific ticker.

```excel wordwrap
=OBB.EQUITY.PRICE.HISTORICAL(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp, intrinio, polygon, tiingo | true |
| interval | string | Time interval of the data to return. | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| limit | number | Number of days to look back (Only for interval 1d). (provider: fmp); The number of data entries to return. (provider: polygon) | true |
| start_time | string | Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'. (provider: intrinio) | true |
| end_time | string | Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'. (provider: intrinio) | true |
| timezone | string | Timezone of the data, in the IANA format (Continent/City). (provider: intrinio) | true |
| source | string | The source of the data. (provider: intrinio) | true |
| sort | string | Sort order of the data. (provider: polygon) | true |
| adjusted | boolean | Output time series is adjusted by historical split and dividend events. (provider: polygon) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| open | The open price.  |
| high | The high price.  |
| low | The low price.  |
| close | The close price.  |
| volume | The trading volume.  |
| vwap | Volume Weighted Average Price over the period.  |
| label | Human readable format of the date. (provider: fmp) |
| adj_close | Adjusted Close Price of the symbol. (provider: fmp);
    Adjusted closing price during the period. (provider: intrinio);
    Adjusted closing price during the period. (provider: tiingo) |
| unadjusted_volume | Unadjusted volume of the symbol. (provider: fmp) |
| change | Change in the price of the symbol from the previous day. (provider: fmp, intrinio) |
| change_percent | Change % in the price of the symbol. (provider: fmp) |
| change_over_time | Change % in the price of the symbol over a period of time. (provider: fmp) |
| close_time | The timestamp that represents the end of the interval span. (provider: intrinio) |
| interval | The data time frequency. (provider: intrinio) |
| average | Average trade price of an individual equity during the interval. (provider: intrinio) |
| intra_period | If true, the equity price represents an unfinished period (be it day, week, quarter, month, or year), meaning that the close price is the latest price available, not the official close price for the period (provider: intrinio) |
| adj_open | Adjusted open price during the period. (provider: intrinio, tiingo) |
| adj_high | Adjusted high price during the period. (provider: intrinio, tiingo) |
| adj_low | Adjusted low price during the period. (provider: intrinio, tiingo) |
| adj_volume | Adjusted volume during the period. (provider: intrinio, tiingo) |
| factor | factor by which to multiply equity prices before this date, in order to calculate historically-adjusted equity prices. (provider: intrinio) |
| split_ratio | Ratio of the equity split, if a equity split occurred. (provider: intrinio, tiingo) |
| dividend | Dividend amount, if a dividend was paid. (provider: intrinio, tiingo) |
| percent_change | Percent change in the price of the symbol from the previous day. (provider: intrinio) |
| fifty_two_week_high | 52 week high price for the symbol. (provider: intrinio) |
| fifty_two_week_low | 52 week low price for the symbol. (provider: intrinio) |
| transactions | Number of transactions for the symbol in the time period. (provider: polygon) |
