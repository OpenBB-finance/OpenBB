---
title: peers
description: Learn how to compare and analyze equity peers with the `obb.equity.compare.peers`
  function. This function allows you to retrieve a list of company peers based on
  symbol, sector, exchange, and market cap. Understand the parameters, returns, and
  data structure provided by this function.
keywords: 
- equity peers
- company peers
- compare peers
- symbol
- provider
- parameter
- returns
- data
- list of peers
- sector
- exchange
- market cap
- serializable results
- chart object
- metadata
- command execution
- warnings
---

<!-- markdownlint-disable MD041 -->

Equity Peers. Company peers.

## Syntax

```excel wordwrap
=OBB.EQUITY.COMPARE.PEERS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| peers_list | A list of equity peers based on sector, exchange and market cap.  |
