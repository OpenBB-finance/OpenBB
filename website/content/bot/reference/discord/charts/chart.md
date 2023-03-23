---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: chart
description: OpenBB Discord Command
---

# chart

Shows the candlestick chart for the ticker/interval provided

### Usage

```python wordwrap
/chart ticker interval [past_days] [extended_hours]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| interval | Chart Interval | False | Daily (1440), Weekly (7200), Monthly (28800), 1 minute (1), 5 minute (5), 10 minute (10), 15 minute (15), 30 minute (30), 1 hour (60) |
| past_days | Past Days to Display. Default: 0 | True | None |
| extended_hours | Display Full 4am-8pm ET Trading Hours. Default: False | True | None |


---

## Examples

```
/chart ticker:AMD interval:5 minute past_days:0
```

```
/chart ticker:AMD interval:Daily
```

---
