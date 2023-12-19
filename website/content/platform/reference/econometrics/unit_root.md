---
title: unit_root
description: Learn how to use the Augmented Dickey-Fuller unit root test to check
  for stationarity in time series data. This function takes in an input dataset and
  performs the test on specified data columns. The regression type can be customized,
  and the function returns the results.
keywords:
- Augmented Dickey-Fuller
- unit root test
- data
- data columns
- unit root
- regression
- constant
- trend
- trend-squared
- results
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Perform Augmented Dickey-Fuller unit root test.

Parameters
----------
data: List[Data]
Input dataset.
column: str
Data columns to check unit root
regression: str
Regression type to use in the test.  Either "c" for constant only, "ct" for constant and trend, or "ctt" for
constant, trend, and trend-squared.

Returns
-------
OBBject[Data]
OBBject with the results being the score from the test.

```python wordwrap

```

---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

