---
title: HISTORICAL
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

Cryptocurrency Historical Price. Cryptocurrency historical price data.

## Syntax

```excel wordwrap
=OBB.CRYPTO.PRICE.HISTORICAL(symbol;[start_date];[end_date];[provider];[timeseries];[interval];[multiplier];[timespan];[sort];[limit];[adjusted];[exchanges])
```

### Example

```excel wordwrap
=OBB.CRYPTO.PRICE.HISTORICAL("BTCUSD")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for. Can use CURR1-CURR2 or CURR1CURR2 format.** | **True** |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: fmp, polygon, tiingo, defaults to fmp. | False |
| timeseries | Number | Number of days to look back. (provider: fmp) | False |
| interval | Text | Data granularity. (provider: fmp, tiingo) | False |
| multiplier | Number | Multiplier of the timespan. (provider: polygon) | False |
| timespan | Text | Timespan of the data. (provider: polygon) | False |
| sort | Text | Sort order of the data. (provider: polygon) | False |
| limit | Number | The number of data entries to return. (provider: polygon) | False |
| adjusted | Boolean | Whether the data is adjusted. (provider: polygon) | False |
| exchanges | Any | To limit the query to a subset of exchanges e.g. ['POLONIEX', 'GDAX'] (provider: tiingo) | False |

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
| vwap | Volume Weighted Average Price over the period.  |
| adj_close | The adjusted close price. (provider: fmp) |
| unadjusted_volume | Unadjusted volume of the symbol. (provider: fmp) |
| change | Change in the price of the symbol from the previous day. (provider: fmp) |
| change_percent | Change % in the price of the symbol. (provider: fmp) |
| label | Human readable format of the date. (provider: fmp) |
| change_over_time | Change % in the price of the symbol over a period of time. (provider: fmp) |
| transactions | Number of transactions for the symbol in the time period. (provider: polygon, tiingo) |
| volume_notional | The last size done for the asset on the specific date in the quote currency. The volume of the asset on the specific date in the quote currency. (provider: tiingo) |
