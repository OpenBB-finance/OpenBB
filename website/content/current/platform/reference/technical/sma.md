---
title: sma
description: Learn about the Simple Moving Average and how it can be used to smooth
  data, eliminate noise, and identify trends. Gain insights into the simple form of
  moving averages, equal weighting, responsiveness to changes, and filtering data.
  Understand the parameters involved in the calculation, such as length and offset.
keywords:
- Simple Moving Average
- moving averages
- smoothing data
- identify trends
- noise elimination
- simplest form of moving average
- equal weight
- responsive to changes
- filtering data
- data calculation
- length parameter
- offset parameter
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Simple Moving Average.

Moving Averages are used to smooth the data in an array to
help eliminate noise and identify trends. The Simple Moving Average is literally
the simplest form of a moving average. Each output value is the average of the
previous n values. In a Simple Moving Average, each value in the time period carries
equal weight, and values outside of the time period are not included in the average.
This makes it less responsive to recent changes in the data, which can be useful for
filtering out those changes.

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
Offset from the current period, by default 0.

Returns
-------
OBBject[List[Data]]
The calculated data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
sma_data = obb.technical.sma(data=stock_data.results,target="close",length=50,offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

