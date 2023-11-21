---
title: atr
description: Learn about the Average True Range indicator used to measure volatility
  in financial data and how to apply it with examples.
keywords:
- Average True Range
- volatility measurement
- gaps
- limit moves
- data
- index column
- length
- moving average mode
- difference period
- offset
- OBBject
- List
- examples
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Average True Range.

Used to measure volatility, especially volatility caused by gaps or limit moves.

Parameters
----------
data : List[Data]
List of data to apply the indicator to.
index : str, optional
Index column name, by default "date"
length : PositiveInt, optional
It's period, by default 14
mamode : Literal["rma", "ema", "sma", "wma"], optional
Moving average mode, by default "rma"
drift : NonNegativeInt, optional
The difference period, by default 1
offset : int, optional
How many periods to offset the result, by default 0

Returns
-------
OBBject[List[Data]]
List of data with the indicator applied.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
atr_data = obb.technical.atr(data=stock_data.results)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

