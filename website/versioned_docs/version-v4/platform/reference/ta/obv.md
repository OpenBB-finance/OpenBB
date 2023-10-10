---
title: obv
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# obv

The On Balance Volume (OBV) is a cumulative total of the up and
    down volume. When the close is higher than the previous close, the volume is added
    to the running total, and when the close is lower than the previous close, the volume
    is subtracted from the running total.

    To interpret the OBV, look for the OBV to move with the price or precede price moves.
    If the price moves before the OBV, then it is a non-confirmed move. A series of rising peaks,
    or falling troughs, in the OBV indicates a strong trend. If the OBV is flat, then the market
    is not trending.

    Parameters
    ----------
    data : List[Data]
        List of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    offset : int, optional
        How many periods to offset the result, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        List of data with the indicator applied.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> obv_data = obb.ta.obv(data=stock_data.results, offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

