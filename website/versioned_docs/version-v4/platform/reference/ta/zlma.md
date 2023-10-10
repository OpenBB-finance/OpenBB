---
title: zlma
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# zlma

The zero lag exponential moving average (ZLEMA) indicator
    was created by John Ehlers and Ric Way. The idea is do a
    regular exponential moving average (EMA) calculation but
    on a de-lagged data instead of doing it on the regular data.
    Data is de-lagged by removing the data from "lag" days ago
    thus removing (or attempting to) the cumulative effect of
    the moving average.

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
        Offset to be used for the calculation, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> zlma_data = obb.ta.zlma(data=stock_data.results, target="close", length=50, offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

