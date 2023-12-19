---
title: clenow
description: Learn about Clenow Volatility Adjusted Momentum and how to calculate
  it using Python code with openbb library. Explore the parameters, examples, and
  returns of this technical analysis function.
keywords:
- Clenow Volatility Adjusted Momentum
- Clenow
- momentum
- data
- index column
- target column
- period
- calculation
- examples
- Python code
- openbb
- equity
- price
- historical
- symbol
- start date
- provider
- technical analysis
- stock data
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Clenow Volatility Adjusted Momentum.

Parameters
----------
data : List[Data]
List of data to be used for the calculation.
index : str, optional
Index column name to use with `data`, by default "date".
target : str, optional
Target column name, by default "close".
period : PositiveInt, optional
Number of periods for the momentum, by default 90.

Returns
-------
OBBject[List[Data]]
The calculated data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
clenow_data = obb.technical.clenow(data=stock_data.results,period=90)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

