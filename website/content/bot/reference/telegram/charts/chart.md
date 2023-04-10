---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: chart
description: OpenBB Telegram Command
---

# chart

This command will retrieve a candlestick chart for the ticker/interval provided, with data for the past number of days specified. The interval provided must be a valid time interval (e.g. 5 minute, 15 minute, etc.). The chart will be displayed to the user and will contain information such as the opening and closing prices, the high and low, the volume, and any other relevant information.

### Usage

```python wordwrap
/chart ticker interval [past_days]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| interval | `1m`, `5m`, `10m`, `15m`, `30m`, `60m`, `1d`, `1wk`, `1mo` Default: `15m` | False | 1d, 1wk, 1mo, 1m, 5m, 10m, 15m, 30m, 1hr |
| past_days | Past Days to Display. Default: 0 | True | None |


---

## Examples

```
/chart AMD 1d 10
```

```
/chart AMD 1d
```

---
