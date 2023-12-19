---
title: kc
description: Learn how to use Keltner Channels, volatility-based bands used to determine
  the direction of a trend. This documentation covers the Keltner Channels calculation,
  breakout signals, and parameters like the moving average mode, length, scalar value,
  and offset.
keywords:
- Keltner Channels
- volatility-based bands
- direction of a trend
- average true range
- ATR
- breakout signals
- Keltner Channels calculation
- moving average mode
- length of Keltner Channels
- scalar value for Keltner Channels
- offset for Keltner Channels
- Keltner Channels data
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Keltner Channels.

Keltner Channels are volatility-based bands that are placed
on either side of an asset's price and can aid in determining
the direction of a trend.The Keltner channel uses the average
true range (ATR) or volatility, with breaks above or below the top
and bottom barriers signaling a continuation.

Parameters
----------
data : List[Data]
The data to use for the Keltner Channels calculation.
index : str, optional
Index column name to use with `data`, by default "date"
length : PositiveInt, optional
The length of the Keltner Channels, by default 20
scalar : PositiveFloat, optional
The scalar to use for the Keltner Channels, by default 20
mamode : Literal["ema", "sma", "wma", "hma", "zlma"], optional
The moving average mode to use for the Keltner Channels, by default "ema"
offset : NonNegativeInt, optional
The offset to use for the Keltner Channels, by default 0

Returns
-------
OBBject[List[Data]]
The Keltner Channels data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
kc_data = obb.technical.kc(data=stock_data.results, length=20, scalar=20, mamode="ema", offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

