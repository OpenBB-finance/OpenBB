---
title: rsi
description: Learn about Relative Strength Index (RSI) and how to calculate it. Understand
  its interpretation as an overbought/oversold indicator and its relevance in identifying
  price movements and reversals. Explore the various parameters involved in the RSI
  calculation with practical examples.
keywords:
- Relative Strength Index
- RSI
- oversold indicator
- overbought indicator
- divergence
- price movements
- reversal
- parameters
- data
- target
- index
- length
- scalar
- drift
- examples
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Relative Strength Index (RSI).

RSI calculates a ratio of the recent upward price movements to the absolute price
movement. The RSI ranges from 0 to 100.
The RSI is interpreted as an overbought/oversold indicator when
the value is over 70/below 30. You can also look for divergence with price. If
the price is making new highs/lows, and the RSI is not, it indicates a reversal.

Parameters
----------
data : List[Data]
The data to use for the RSI calculation.
target : str
Target column name.
index : str, optional
Index column name to use with `data`, by default "date"
length : int, optional
The length of the RSI, by default 14
scalar : float, optional
The scalar to use for the RSI, by default 100.0
drift : int, optional
The drift to use for the RSI, by default 1

Returns
-------
OBBject[List[Data]]
The RSI data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
rsi_data = obb.technical.rsi(data=stock_data.results, target="close", length=14, scalar=100.0, drift=1)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

