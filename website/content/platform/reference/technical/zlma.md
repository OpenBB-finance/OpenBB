---
title: zlma
description: Learn about the zero lag exponential moving average (ZLEMA) and how it
  can be used to perform EMA calculations on de-lagged data. Explore the parameters
  and get examples of implementing ZLEMA in Python.
keywords:
- zero lag exponential moving average
- ZLEMA
- EMA calculation
- de-lagged data
- moving average
- lagged data
- cumulative effect
- parameters
- target column
- index column
- length
- offset
- calculation
- calculated data
- example
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The zero lag exponential moving average (ZLEMA).

Created by John Ehlers and Ric Way. The idea is do a
regular exponential moving average (EMA) calculation but
on a de-lagged data instead of doing it on the regular data.
Data is de-lagged by removing the data from "lag" days ago
thus removing (or attempting to) the cumulative effect of
the moving average.

Parameters
----------
data : List[Data]
List of data to be used for the calculation.
target : str
Target column name.
index : str, optional
Index column name to use with `data`, by default "date".
length : int, optional
Number of periods to be used for the calculation, by default 50.
offset : int, optional
Offset to be used for the calculation, by default 0.

Returns
-------
OBBject[List[Data]]
The calculated data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
zlma_data = obb.technical.zlma(data=stock_data.results, target="close", length=50, offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

