---
title: fib
description: Learn how to create Fibonacci Retracement Levels using the openbb Python
  library for technical analysis. Apply the Fibonacci indicator to stock data and
  visualize the results.
keywords:
- Fibonacci Retracement Levels
- Fibonacci indicator
- technical analysis
- stock data
- Python
- data visualization
- open source library
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Create Fibonacci Retracement Levels.

Parameters
----------
data : List[Data]
List of data to apply the indicator to.
index : str, optional
Index column name, by default "date"
period : PositiveInt, optional
Period to calculate the indicator, by default 120

Returns
-------
OBBject[List[Data]]
List of data with the indicator applied.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
fib_data = obb.technical.fib(data=stock_data.results, period=120)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

