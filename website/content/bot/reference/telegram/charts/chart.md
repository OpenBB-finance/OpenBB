---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: chart
description: OpenBB Telegram Command
---

# chart

Shows the candlestick chart for the ticker/interval provided

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
