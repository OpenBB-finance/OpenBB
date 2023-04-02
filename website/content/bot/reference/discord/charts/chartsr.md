---
########### THIS FILE IS AUTO GENERATED - ANY CHANGES WILL BE VOID ###########
title: chartsr
description: OpenBB Discord Command
---

# chartsr

This command allows the user to retrieve Displays Support and Resistance Levels for the ticker provided. It will display the support and resistance levels of a given ticker, such as AMC, on a chart. This command uses the data provided by the user to show the support and resistance levels that are likely to be seen in the future. These levels can help the user in making better trading decisions.

### Usage

```python wordwrap
/chartsr ticker [interval]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| ticker | Stock Ticker | False | None |
| interval | Chart Interval | True | 5 minute (5), 15 minute (15) |


---

## Examples

```
/chartsr ticker:AMC
```
```
/chartsr ticker:AMC interval:5 minute
```

---
