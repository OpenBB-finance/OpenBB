---
title: aroon
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# aroon

The word aroon is Sanskrit for "dawn's early light." The Aroon
    indicator attempts to show when a new trend is dawning. The indicator consists
    of two lines (Up and Down) that measure how long it has been since the highest
    high/lowest low has occurred within an n period range.

    When the Aroon Up is staying between 70 and 100 then it indicates an upward trend.
    When the Aroon Down is staying between 70 and 100 then it indicates an downward trend.
    A strong upward trend is indicated when the Aroon Up is above 70 while the Aroon Down is below 30.
    Likewise, a strong downward trend is indicated when the Aroon Down is above 70 while
    the Aroon Up is below 30. Also look for crossovers. When the Aroon Down crosses above
    the Aroon Up, it indicates a weakening of the upward trend (and vice versa).

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index: str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods to be used for the calculation, by default 25.
    scalar : int, optional
        Scalar to be used for the calculation, by default 100.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> aroon_data = obb.ta.aroon(data=stock_data.results, length=25, scalar=100)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

