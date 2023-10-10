---
title: sma
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sma

Moving Averages are used to smooth the data in an array to
    help eliminate noise and identify trends. The Simple Moving Average is literally
    the simplest form of a moving average. Each output value is the average of the
    previous n values. In a Simple Moving Average, each value in the time period carries
    equal weight, and values outside of the time period are not included in the average.
    This makes it less responsive to recent changes in the data, which can be useful for
    filtering out those changes.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods to be used for the calculation, by default 50.
    offset : int, optional
        Offset from the current period, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> sma_data = obb.ta.sma(data=stock_data.results,target="close",length=50,offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

