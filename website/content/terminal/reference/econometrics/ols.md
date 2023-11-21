---
title: ols
description: This page explains how to perform an OLS regression on timeseries data
  using specific commands and parameters. It's useful for those working in data analytics
  or statistical modeling.
keywords:
- OLS regression
- timeseries data
- data analytics
- statistical modeling
- dependent variable
- independent variable
- no_output parameter
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics /ols - Reference | OpenBB Terminal Docs" />

Performs an OLS regression on timeseries data.

### Usage

```python wordwrap
ols -d DEPENDENT -i INDEPENDENT [--no-output]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| dependent | -d  --dependent | The dependent variable on the regression you would like to perform | None | False | None |
| independent | -i  --independent | The independent variables on the regression you would like to perform. E.g. historical.high,historical.low | None | False | None |
| no_output | --no-output | Hide the output of the regression | False | True | None |

---
