---
title: unitroot_test
description: Learn about the Unit Root Test function in Python, including the Augmented
  Dickey-Fuller test and the Kwiatkowski-Phillips-Schmidt-Shin test. Explore the parameters,
  such as data, target, fuller_reg, and kpss_reg, and understand how to interpret
  the unit root tests summary.
keywords:
- Unit Root Test
- Augmented Dickey-Fuller test
- Kwiatkowski-Phillips-Schmidt-Shin test
- data
- target
- fuller_reg
- kpss_reg
- Time series data
- unit root tests
- unit root tests summary
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get Unit Root Test.

Augmented Dickey-Fuller test for unit root.
Kwiatkowski-Phillips-Schmidt-Shin test for unit root.

Parameters
----------
data : List[Data]
Time series data.
target : str
Target column name.
fuller_reg : Literal["c", "ct", "ctt", "nc", "c"]
Regression type for ADF test.
kpss_reg : Literal["c", "ct"]
Regression type for KPSS test.

Returns
-------
OBBject[UnitRootModel]
Unit root tests summary.

```python wordwrap

```

---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

