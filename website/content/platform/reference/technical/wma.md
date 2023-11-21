---
title: wma
description: Learn about the Weighted Moving Average (WMA) and how it is used to give
  more weight to recent data. Understand its unique calculation and how it compares
  to the Simple Moving Average. Find out the parameters for the WMA function, such
  as the target and index column names, length, and offset. See an example of using
  the WMA function in Python with the OpenBB library to calculate WMA data for historical
  stock prices.
keywords:
- weighted moving average
- WMA
- moving average
- weighting factor
- price
- data
- calculation
- simple moving average
- parameters
- target column
- index column
- length
- offset
- returns
- examples
- python
- openbb
- equity
- price
- historical
- symbol
- start date
- provider
- wma data
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Weighted Moving Average.

A Weighted Moving Average puts more weight on recent data and less on past data.
This is done by multiplying each bar's price by a weighting factor. Because of its
unique calculation, WMA will follow prices more closely than a corresponding Simple
Moving Average.

Parameters
----------
data : List[Data]
The data to use for the calculation.
target : str
Target column name.
index : str, optional
Index column name to use with `data`, by default "date".
length : int, optional
The length of the WMA, by default 50.
offset : int, optional
The offset of the WMA, by default 0.

Returns
-------
OBBject[List[Data]]
The WMA data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
wma_data = obb.technical.wma(data=stock_data.results, target="close", length=50, offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

