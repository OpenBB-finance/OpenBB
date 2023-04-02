---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: cc
description: OpenBB Discord Command
---

# cc

This command allows the user to retrieve intraday 5-minute charts for a given ticker. The command /c5m or /cc ticker:AMD can be used to retrieve the chart, with the ticker being the symbol of the stock or other security. The resulting chart will contain the intraday price data for the given ticker for the current day.

### Usage

```python wordwrap
/cc ticker [extended_hours]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| extended_hours | Show Full 4am-8pm ET Trading Hours. Default: False | True | None |


---

## Examples

```
/cc ticker:AMD
```

---
