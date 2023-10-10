---
title: cg
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cg

The Center of Gravity indicator, in short, is used to anticipate future price movements
    and to trade on price reversals as soon as they happen. However, just like other oscillators,
    the COG indicator returns the best results in range-bound markets and should be avoided when
    the price is trending. Traders who use it will be able to closely speculate the upcoming
    price change of the asset.

    Parameters
    ----------
    data : List[Data]
        The data to use for the COG calculation.
    index : str, optional
        Index column name to use with `data`, by default "date"
    length : PositiveInt, optional
        The length of the COG, by default 14

    Returns
    -------
    OBBject[List[Data]]
        The COG data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> cg_data = obb.ta.cg(data=stock_data.results, length=14)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

