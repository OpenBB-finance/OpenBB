---
title: unusual
description: Learn how to get the complete options chain for a ticker with the equity
  options unusual API. Explore the available parameters such as symbol and provider.
  Retrieve valuable data like the underlying symbol, contract symbol, trade type,
  sentiment, total value, total size, average price, ask/bid prices at execution,
  underlying price at execution, and timestamp.
keywords: 
- complete options chain
- ticker options
- equity options unusual
- symbol
- provider
- intrinio
- source
- data
- underlying symbol
- contract symbol
- trade type
- sentiment
- total value
- total size
- average price
- ask at execution
- bid at execution
- underlying price at execution
- timestamp
---

<!-- markdownlint-disable MD041 -->

Get the complete options chain for a ticker.

## Syntax

```excel wordwrap
=OBB.DERIVATIVES.OPTIONS.UNUSUAL(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: intrinio | True |
| symbol | Text | Symbol to get data for. (the underlying symbol) | True |
| source | Text | The source of the data. Either realtime or delayed. (provider: intrinio) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| underlying_symbol | Symbol representing the entity requested in the data. (the underlying symbol)  |
| contract_symbol | Contract symbol for the option.  |
| trade_type | The type of unusual trade. (provider: intrinio) |
| sentiment | Bullish, Bearish, or Neutral Sentiment is estimated based on whether the trade was executed at the bid, ask, or mark price. (provider: intrinio) |
| total_value | The aggregated value of all option contract premiums included in the trade. (provider: intrinio) |
| total_size | The total number of contracts involved in a single transaction. (provider: intrinio) |
| average_price | The average premium paid per option contract. (provider: intrinio) |
| ask_at_execution | Ask price at execution. (provider: intrinio) |
| bid_at_execution | Bid price at execution. (provider: intrinio) |
| underlying_price_at_execution | Price of the underlying security at execution of trade. (provider: intrinio) |
| timestamp | The UTC timestamp of order placement. (provider: intrinio) |
