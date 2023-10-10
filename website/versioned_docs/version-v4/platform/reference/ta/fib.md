---
title: fib
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fib

Create Fibonacci Retracement Levels.

    Parameters
    ----------
    data : List[Data]
        List of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    period : PositiveInt, optional
        Period to calculate the indicator, by default 120

    Returns
    -------
    OBBject[List[Data]]
        List of data with the indicator applied.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> fib_data = obb.ta.fib(data=stock_data.results, period=120)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

