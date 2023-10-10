---
title: ema
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ema

The Exponential Moving Average is a staple of technical
    analysis and is used in countless technical indicators. In a Simple Moving
    Average, each value in the time period carries equal weight, and values outside
    of the time period are not included in the average. However, the Exponential
    Moving Average is a cumulative calculation, including all data. Past values have
    a diminishing contribution to the average, while more recent values have a greater
    contribution. This method allows the moving average to be more responsive to changes
    in the data.

    Parameters
    ----------
    data : List[Data]
        The data to use for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date"
    length : int, optional
        The length of the calculation, by default 50.
    offset : int, optional
        The offset of the calculation, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> ema_data = obb.ta.ema(data=stock_data.results,target="close",length=50,offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

