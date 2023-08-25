---
title: ols
description: OpenBB Terminal Function
---

# ols

Performs an OLS regression on timeseries data.

### Usage

```python
ols -d DEPENDENT -i INDEPENDENT [--no-output]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| dependent | The dependent variable on the regression you would like to perform | None | False | None |
| independent | The independent variables on the regression you would like to perform. E.g. historical.high,historical.low | None | False | None |
| no_output | Hide the output of the regression | False | True | None |

---
