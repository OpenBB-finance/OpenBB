---
title: clenow
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# clenow

Clenow Volatility Adjusted Momentum.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    target : str, optional
        Target column name, by default "adj_close".
    period : PositiveInt, optional
        Number of periods for the momentum, by default 90.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> clenow_data = obb.ta.clenow(data=stock_data.results,period=90)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

