---
title: market_snapshots
description: Get a current, complete market snapshot with the obb.equity.market_snapshots
  Python method. Retrieve equity data such as stock information, financial data, market
  analysis, and trading volume. Explore details like stock performance, price change,
  moving averages, 52-week high and low, market cap, earnings per share, price to
  earnings ratio, and stock exchange.
keywords: 
- market snapshot
- equity data
- market data
- stock information
- financial data
- market analysis
- trading volume
- stock performance
- price change
- moving averages
- 52-week high
- 52-week low
- market cap
- earnings per share
- price to earnings ratio
- stock exchange
---

<!-- markdownlint-disable MD041 -->

Get a current, complete, market snapshot.

## Syntax

```excel wordwrap
=OBB.EQUITY.MARKET_SNAPSHOTS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp, polygon | True |
| market | Text | The market to fetch data for. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| open | The open price.  |
| high | The high price.  |
| low | The low price.  |
| close | The close price.  |
| prev_close | The previous closing price of the stock.  |
| change | The change in price.  |
| change_percent | The change, as a percent.  |
| volume | The trading volume.  |
| price | The last price of the stock. (provider: fmp) |
| avg_volume | Average volume of the stock. (provider: fmp) |
| ma50 | The 50-day moving average. (provider: fmp) |
| ma200 | The 200-day moving average. (provider: fmp) |
| year_high | The 52-week high. (provider: fmp) |
| year_low | The 52-week low. (provider: fmp) |
| market_cap | Market cap of the stock. (provider: fmp) |
| shares_outstanding | Number of shares outstanding. (provider: fmp) |
| eps | Earnings per share. (provider: fmp) |
| pe | Price to earnings ratio. (provider: fmp) |
| exchange | The exchange of the stock. (provider: fmp) |
| timestamp | The timestamp of the data. (provider: fmp) |
| earnings_announcement | The earnings announcement of the stock. (provider: fmp) |
| name | The name associated with the stock symbol. (provider: fmp) |
| vwap | The volume weighted average price of the stock on the current trading day. (provider: polygon) |
| prev_open | The previous trading session opening price. (provider: polygon) |
| prev_high | The previous trading session high price. (provider: polygon) |
| prev_low | The previous trading session low price. (provider: polygon) |
| prev_volume | The previous trading session volume. (provider: polygon) |
| prev_vwap | The previous trading session VWAP. (provider: polygon) |
| last_updated | The last time the data was updated. (provider: polygon) |
| bid | The current bid price. (provider: polygon) |
| bid_size | The current bid size. (provider: polygon) |
| ask_size | The current ask size. (provider: polygon) |
| ask | The current ask price. (provider: polygon) |
| quote_timestamp | The timestamp of the last quote. (provider: polygon) |
| last_trade_price | The last trade price. (provider: polygon) |
| last_trade_size | The last trade size. (provider: polygon) |
| last_trade_conditions | The last trade condition codes. (provider: polygon) |
| last_trade_exchange | The last trade exchange ID code. (provider: polygon) |
| last_trade_timestamp | The last trade timestamp. (provider: polygon) |
