---
title: ad
description: Learn about the Accumulation/Distribution Line and how it is interpreted
  to detect trends in price movement. Explore its parameters, usage, and see code
  examples.
keywords:
- Accumulation/Distribution Line
- On Balance Volume
- CLV
- divergence
- price
- trending upward
- flat
- flattening of the price
- Parameters
- data
- index
- offset
- Returns
- Examples
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The Accumulation/Distribution Line.

Similar to the On Balance Volume (OBV).
Sums the volume times +1/-1 based on whether the close is higher than the previous
close. The Accumulation/Distribution indicator, however multiplies the volume by the
close location value (CLV). The CLV is based on the movement of the issue within a
single bar and can be +1, -1 or zero.


The Accumulation/Distribution Line is interpreted by looking for a divergence in
the direction of the indicator relative to price. If the Accumulation/Distribution
Line is trending upward it indicates that the price may follow. Also, if the
Accumulation/Distribution Line becomes flat while the price is still rising (or falling)
then it signals an impending flattening of the price.

Parameters
----------
data : List[Data]
List of data to be used for the calculation.
index : str, optional
Index column name to use with `data`, by default "date".
offset : int, optional
Offset of the AD, by default 0.

Returns
-------
OBBject[List[Data]]

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
ad_data = obb.technical.ad(data=stock_data.results,offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

