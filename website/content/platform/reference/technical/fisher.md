---
title: fisher
description: Learn about the Fisher Transform, a technical indicator created by John
  F. Ehlers that converts prices into a Gaussian normal distribution. This indicator
  can help identify extreme prices and turning points in asset prices. Discover how
  to use the Fisher Transform with examples and parameter explanations.
keywords:
- Fisher Transform
- John F. Ehlers
- technical indicator
- Gaussian normal distribution
- extreme prices
- turning points
- price waves
- trend isolation
- indicator parameters
- data
- index column
- Fisher period
- Fisher Signal period
- indicator application
- OBBject
- example
- stock data
- equity
- historical price
- symbol
- start date
- data provider
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fisher Transform.

A technical indicator created by John F. Ehlers that converts prices into a Gaussian
normal distribution. The indicator highlights when prices have moved to an extreme,
based on recent prices.
This may help in spotting turning points in the price of an asset. It also helps
show the trend and isolate the price waves within a trend.

Parameters
----------
data : List[Data]
List of data to apply the indicator to.
index : str, optional
Index column name, by default "date"
length : PositiveInt, optional
Fisher period, by default 14
signal : PositiveInt, optional
Fisher Signal period, by default 1

Returns
-------
OBBject[List[Data]]
List of data with the indicator applied.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
fisher_data = obb.technical.fisher(data=stock_data.results, length=14, signal=1)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

