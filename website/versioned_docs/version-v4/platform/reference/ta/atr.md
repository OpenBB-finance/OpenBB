---
title: atr
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# atr

Average True Range is used to measure volatility, especially volatility caused by
    gaps or limit moves.

    Parameters
    ----------
    data : List[Data]
        List of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    length : PositiveInt, optional
        It's period, by default 14
    mamode : Literal["rma", "ema", "sma", "wma"], optional
        Moving average mode, by default "rma"
    drift : NonNegativeInt, optional
        The difference period, by default 1
    offset : int, optional
        How many periods to offset the result, by default 0

    Returns
    -------
    OBBject[List[Data]]
        List of data with the indicator applied.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> atr_data = obb.ta.atr(data=stock_data.results)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

