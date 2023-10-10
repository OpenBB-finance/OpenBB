---
title: demark
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# demark

Demark sequential indicator

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    target : str, optional
        Target column name, by default "close".
    show_all : bool, optional
        Show 1 - 13. If set to False, show 6 - 9
    asint : bool, optional
        If True, fill NAs with 0 and change type to int, by default True.
    offset : int, optional
        How many periods to offset the result

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> demark_data = obb.ta.demark(data=stock_data.results,offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

