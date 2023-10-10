---
title: wma
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# wma

A Weighted Moving Average puts more weight on recent data and less on past data.
    This is done by multiplying each bar's price by a weighting factor. Because of its
    unique calculation, WMA will follow prices more closely than a corresponding Simple
    Moving Average.

    Parameters
    ----------
    data : List[Data]
        The data to use for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        The length of the WMA, by default 50.
    offset : int, optional
        The offset of the WMA, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The WMA data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> wma_data = obb.ta.wma(data=stock_data.results, target="close", length=50, offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

