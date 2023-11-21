---
title: ema
description: Learn how to calculate the Exponential Moving Average (EMA) in Python
  using the openbb library. Understand its benefits as a cumulative calculation and
  how it maintains data responsiveness. Find details on parameters like data, target
  column, index column, length, and offset. Get code examples to implement EMA calculations
  in your projects.
keywords:
- Exponential Moving Average
- EMA
- cumulative calculation
- moving average
- data responsiveness
- parameters
- target column
- index column
- length
- offset
- calculated data
- examples
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Exponential Moving Average.

EMA is a cumulative calculation, including all data. Past values have
a diminishing contribution to the average, while more recent values have a greater
contribution. This method allows the moving average to be more responsive to changes
in the data.

Parameters
----------
data : List[Data]
The data to use for the calculation.
target : str
Target column name.
index : str, optional
Index column name to use with `data`, by default "date"
length : int, optional
The length of the calculation, by default 50.
offset : int, optional
The offset of the calculation, by default 0.

Returns
-------
OBBject[List[Data]]
The calculated data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
ema_data = obb.technical.ema(data=stock_data.results,target="close",length=50,offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

