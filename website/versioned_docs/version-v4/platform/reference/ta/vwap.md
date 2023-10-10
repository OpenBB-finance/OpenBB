---
title: vwap
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# vwap

The Volume Weighted Average Price that measures the average typical price
    by volume.  It is typically used with intraday charts to identify general direction.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    anchor : str, optional
        Anchor period to use for the calculation, by default "D".
        See Timeseries Offset Aliases below for additional options:
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#timeseries-offset-aliases
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
    >>> vwap_data = obb.ta.vwap(data=stock_data.results,anchor="D",offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

