---
title: adx
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# adx

The ADX is a Welles Wilder style moving average of the Directional Movement Index (DX).
    The values range from 0 to 100, but rarely get above 60. To interpret the ADX, consider
    a high number to be a strong trend, and a low number, a weak trend.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods for the ADX, by default 50.
    scalar : float, optional
        Scalar value for the ADX, by default 100.0.
    drift : int, optional
        Drift value for the ADX, by default 1.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> adx_data = obb.ta.adx(data=stock_data.results,length=50,scalar=100.0,drift=1)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

