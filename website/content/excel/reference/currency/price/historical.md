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

Currency Historical Price. Currency historical data.

```excel wordwrap
=OBB.CURRENCY.PRICE.HISTORICAL(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format. | false |
| provider | string | Options: fmp, polygon, tiingo | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| interval | string | Data granularity. (provider: fmp, tiingo) | true |
| multiplier | number | Multiplier of the timespan. (provider: polygon) | true |
| timespan | string | Timespan of the data. (provider: polygon) | true |
| sort | string | Sort order of the data. (provider: polygon) | true |
| limit | number | The number of data entries to return. (provider: polygon) | true |
| adjusted | boolean | Whether the data is adjusted. (provider: polygon) | true |

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
| adj_close | Adjusted Close Price of the symbol. (provider: fmp) |
| unadjusted_volume | Unadjusted volume of the symbol. (provider: fmp) |
| change | Change in the price of the symbol from the previous day. (provider: fmp) |
| change_percent | Change % in the price of the symbol. (provider: fmp) |
| label | Human readable format of the date. (provider: fmp) |
| change_over_time | Change % in the price of the symbol over a period of time. (provider: fmp) |
| transactions | Number of transactions for the symbol in the time period. (provider: polygon) |
