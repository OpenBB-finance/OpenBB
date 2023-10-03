---
title: aprtoapy
description: OpenBB Terminal Function
---

# aprtoapy

Tool to calculate APY from APR value. Compouding periods, i.e., the number of times compounded per year can be defined with -c argument.

### Usage

```python
aprtoapy [--apr APR] [-c COMPOUNDING] [-n]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| apr | APR value in percentage to convert | 100 | True | range(1, 101) |
| compounding | Number of compounded periods in a year. 12 means compounding monthly | 12 | True | range(1, 101) |
| narrative | Flag to show narrative instead of dataframe | False | True | None |

---
