---
title: hist
description: Learn how to use the 'op hist' command to retrieve the historical price
  of options given certain parameters such as ticker, expiry, strike, option type
  and interval for the past x number of days in chart format. Includes examples and
  descriptions of the parameters.
keywords:
- Stock Ticker
- Expiration Date
- Option Strike Price
- Calls or Puts
- Chart Minute Interval
- Past Days to Display
- op hist command
- historical price of options
- chart format
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="options: hist - Discord Reference | OpenBB Bot Docs" />

This command allows the user to retrieve the historical price of options for the given parameters of a ticker, expiry, strike , option type, and interval for the past x days in a chart format.

### Usage

```python wordwrap
/op hist ticker expiry strike opt_type interval [past_days]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| expiry | Expiration Date YYYY-MM-DD format | False | None |
| strike | Option Strike Price | False | None |
| opt_type | Calls or Puts | False | Calls, Puts |
| interval | Chart Minute Interval, 1440 for Daily | False | 15 (15), 30 (30), 60 (60), 1440 (1440) |
| past_days | Past Days to Display. Default: 5 | True | None |


---

## Examples

```
/op hist ticker:AMD expiry:2022-07-29 strike:80 opt_type:Calls interval:15 past_days:5
```

```
/op hist ticker:AMD expiry:2022-07-29 strike:80 opt_type:Calls interval:15
```

---
