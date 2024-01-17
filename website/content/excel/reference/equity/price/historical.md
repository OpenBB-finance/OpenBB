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

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="EQUITY.PRICE.HISTORICAL | OpenBB Add-in for Excel Docs" />

Equity Historical price. Load stock data for a specific ticker.

## Syntax

```excel wordwrap
=OBB.EQUITY.PRICE.HISTORICAL(symbol;[interval];[start_date];[end_date];[provider];[limit];[sort];[start_time];[end_time];[timezone];[source];[sleep];[adjusted])
```

### Example

```excel wordwrap
=OBB.EQUITY.PRICE.HISTORICAL("AAPL")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| interval | Text | Time interval of the data to return. | False |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: fmp, intrinio, polygon, tiingo, defaults to fmp. | False |
| limit | Number | Number of days to look back (Only for interval 1d). (provider: fmp); The number of results to return per page. (provider: intrinio); The number of data entries to return. (provider: polygon) | False |
| sort | Text | Sort the data in ascending or descending order. (provider: fmp); Sort order of the data. (provider: polygon) | False |
| start_time | Text | Return intervals starting at the specified time on the `start_date` formatted as 'HH:MM:SS'. (provider: intrinio) | False |
| end_time | Text | Return intervals stopping at the specified time on the `end_date` formatted as 'HH:MM:SS'. (provider: intrinio) | False |
| timezone | Text | Timezone of the data, in the IANA format (Continent/City). (provider: intrinio) | False |
| source | Text | The source of the data. (provider: intrinio) | False |
| sleep | Number | Time to sleep between requests to avoid rate limiting. (provider: intrinio) | False |
| adjusted | Boolean | Output time series is adjusted by historical split and dividend events. (provider: polygon) | False |

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
| label | Human readable format of the date. (provider: fmp) |
| adj_close | The adjusted close price. (provider: fmp);     Adjusted closing price during the period. (provider: intrinio);     Adjusted closing price during the period. (provider: tiingo) |
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
