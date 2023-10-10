---
title: hma
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hma

The Hull Moving Average solves the age old dilemma of making a moving average
    more responsive to current price activity whilst maintaining curve smoothness.
    In fact the HMA almost eliminates lag altogether and manages to improve smoothing
    at the same time.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods for the HMA, by default 50.
    offset : int, optional
        Offset of the HMA, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> hma_data = obb.ta.hma(data=stock_data.results,target="close",length=50,offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

