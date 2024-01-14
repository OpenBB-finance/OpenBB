---
title: available
description: Available Indices
keywords: 
- index
- available
---

<!-- markdownlint-disable MD041 -->

Available Indices. Available indices for a given provider.

## Syntax

```jsx<span style={color: 'red'}>=OBB.INDEX.AVAILABLE([provider])</span>```

### Example

```excel wordwrap
=OBB.INDEX.AVAILABLE()
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp, defaults to fmp. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| name | Name of the index.  |
| currency | Currency the index is traded in.  |
| isin | ISIN code for the index. Valid only for European indices. (provider: cboe) |
| region | Region for the index. Valid only for European indices (provider: cboe) |
| symbol | Symbol for the index. (provider: cboe, yfinance) |
| description | Description for the index. Valid only for US indices. (provider: cboe) |
| data_delay | Data delay for the index. Valid only for US indices. (provider: cboe) |
| open_time | Opening time for the index. Valid only for US indices. (provider: cboe) |
| close_time | Closing time for the index. Valid only for US indices. (provider: cboe) |
| time_zone | Time zone for the index. Valid only for US indices. (provider: cboe) |
| tick_days | The trading days for the index. Valid only for US indices. (provider: cboe) |
| tick_frequency | The frequency of the index ticks. Valid only for US indices. (provider: cboe) |
| tick_period | The period of the index ticks. Valid only for US indices. (provider: cboe) |
| stock_exchange | Stock exchange where the index is listed. (provider: fmp) |
| exchange_short_name | Short name of the stock exchange where the index is listed. (provider: fmp) |
| code | ID code for keying the index in the OpenBB Terminal. (provider: yfinance) |
