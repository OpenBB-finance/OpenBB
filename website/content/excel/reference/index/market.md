---
title: market
description: Learn how to retrieve historical market indices data using various data
  providers and query parameters. Understand the available parameters and return values,
  such as symbol, start date, end date, provider, interval, timeseries, timespan,
  sort order, limit, adjusted, multiplier, chart, metadata, date, open price, high
  price, low price, close price, volume, calls volume, puts volume, options volume,
  adjusted close price, unadjusted volume, change, change percent, label, change over
  time, and transactions.
keywords: 
- Historical Market Indices
- market data
- symbol
- start date
- end date
- data provider
- query
- interval
- timeseries
- timespan
- sort order
- limit
- adjusted
- multiplier
- chart
- metadata
- date
- open price
- high price
- low price
- close price
- volume
- calls volume
- puts volume
- options volume
- adjusted close price
- unadjusted volume
- change
- change percent
- label
- change over time
- transactions
---

<!-- markdownlint-disable MD041 -->

Historical Market Indices.

```excel wordwrap
=OBB.INDEX.MARKET(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp, intrinio, polygon | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| timeseries | number | Number of days to look back. (provider: fmp) | true |
| interval | string | Data granularity. (provider: fmp) | true |
| tag | string | Index tag. (provider: intrinio) | true |
| type | string | Index type. (provider: intrinio) | true |
| sort | string | Sort order. (provider: intrinio); Sort order of the data. (provider: polygon) | true |
| limit | number | The number of data entries to return. (provider: intrinio, polygon) | true |
| timespan | string | Timespan of the data. (provider: polygon) | true |
| adjusted | boolean | Whether the data is adjusted. (provider: polygon) | true |
| multiplier | number | Multiplier of the timespan. (provider: polygon) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| open | The open price.  |
| high | The high price.  |
| low | The low price.  |
| close | The close price.  |
| volume | The trading volume.  |
| adj_close | Adjusted Close Price of the symbol. (provider: fmp) |
| unadjusted_volume | Unadjusted volume of the symbol. (provider: fmp) |
| change | Change in the price of the symbol from the previous day. (provider: fmp) |
| change_percent | Change % in the price of the symbol. (provider: fmp) |
| label | Human readable format of the date. (provider: fmp) |
| change_over_time | Change % in the price of the symbol over a period of time. (provider: fmp) |
| transactions | Number of transactions for the symbol in the time period. (provider: polygon) |
