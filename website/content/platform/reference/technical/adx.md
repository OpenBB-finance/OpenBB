---
title: adx
description: Learn about ADX, a Welles Wilder style moving average of the Directional
  Movement Index. Understand its calculation, interpretation, and usage with stock
  data. Explore examples for implementation.
keywords:
- ADX
- Welles Wilder
- moving average
- Directional Movement Index
- trend
- calculation
- data
- index column
- length
- scalar value
- drift
- interpretation
- stock data
- historical data
- examples
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

ADX.

The ADX is a Welles Wilder style moving average of the Directional Movement Index (DX).
The values range from 0 to 100, but rarely get above 60. To interpret the ADX, consider
a high number to be a strong trend, and a low number, a weak trend.

Parameters
----------
data : List[Data]
List of data to be used for the calculation.
index : str, optional
Index column name to use with `data`, by default "date".
length : int, optional
Number of periods for the ADX, by default 50.
scalar : float, optional
Scalar value for the ADX, by default 100.0.
drift : int, optional
Drift value for the ADX, by default 1.

Returns
-------
OBBject[List[Data]]
The calculated data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
adx_data = obb.technical.adx(data=stock_data.results,length=50,scalar=100.0,drift=1)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

