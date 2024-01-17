---
title: MARKET
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

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="INDEX.MARKET | OpenBB Add-in for Excel Docs" />

Historical Market Indices.

## Syntax

```excel wordwrap
=OBB.INDEX.MARKET(symbol;[start_date];[end_date];[provider];[timeseries];[interval];[sort];[tag];[type];[limit];[sleep];[timespan];[adjusted];[multiplier])
```

### Example

```excel wordwrap
=OBB.INDEX.MARKET("^GSPC")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: fmp, intrinio, polygon, defaults to fmp. | False |
| timeseries | Number | Number of days to look back. (provider: fmp) | False |
| interval | Text | Data granularity. (provider: fmp) | False |
| sort | Text | Sort the data in ascending or descending order. (provider: fmp); Sort order. (provider: intrinio); Sort order of the data. (provider: polygon) | False |
| tag | Text | Index tag. (provider: intrinio) | False |
| type | Text | Index type. (provider: intrinio) | False |
| limit | Number | The number of data entries to return. (provider: intrinio, polygon) | False |
| sleep | Number | Time to sleep between requests to avoid rate limiting. (provider: intrinio) | False |
| timespan | Text | Timespan of the data. (provider: polygon) | False |
| adjusted | Boolean | Whether the data is adjusted. (provider: polygon) | False |
| multiplier | Number | Multiplier of the timespan. (provider: polygon) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| open | The open price.  |
| high | The high price.  |
| low | The low price.  |
| close | The close price.  |
| volume | The trading volume.  |
| adj_close | The adjusted close price. (provider: fmp) |
| unadjusted_volume | Unadjusted volume of the symbol. (provider: fmp) |
| change | Change in the price of the symbol from the previous day. (provider: fmp) |
| change_percent | Change % in the price of the symbol. (provider: fmp) |
| label | Human readable format of the date. (provider: fmp) |
| change_over_time | Change % in the price of the symbol over a period of time. (provider: fmp) |
| transactions | Number of transactions for the symbol in the time period. (provider: polygon) |
