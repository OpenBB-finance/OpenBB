---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: hist
description: OpenBB Discord Command
---

# hist

Displays Options Price History in a chart.

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
