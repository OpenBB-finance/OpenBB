---
title: obv
description: Learn about On Balance Volume (OBV), a cumulative volume indicator that
  helps to interpret price moves, identify trends, and determine market trends. This
  documentation page provides an explanation of how OBV works, its parameters, and
  a Python example.
keywords:
- On Balance Volume
- OBV
- cumulative volume
- up and down volume
- running total
- price moves
- non-confirmed move
- rising peaks
- falling troughs
- strong trend
- flat OBV
- interpret OBV
- how to use OBV
- Python example
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

On Balance Volume (OBV).

Is a cumulative total of the up and down volume. When the close is higher than the
previous close, the volume is added to the running total, and when the close is
lower than the previous close, the volume is subtracted from the running total.

To interpret the OBV, look for the OBV to move with the price or precede price moves.
If the price moves before the OBV, then it is a non-confirmed move. A series of rising peaks,
or falling troughs, in the OBV indicates a strong trend. If the OBV is flat, then the market
is not trending.

Parameters
----------
data : List[Data]
List of data to apply the indicator to.
index : str, optional
Index column name, by default "date"
offset : int, optional
How many periods to offset the result, by default 0.

Returns
-------
OBBject[List[Data]]
List of data with the indicator applied.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
obv_data = obb.technical.obv(data=stock_data.results, offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

