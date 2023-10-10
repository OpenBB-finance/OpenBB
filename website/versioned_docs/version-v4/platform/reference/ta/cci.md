---
title: cci
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cci

The CCI is designed to detect beginning and ending market trends.
    The range of 100 to -100 is the normal trading range. CCI values outside of this
    range indicate overbought or oversold conditions. You can also look for price
    divergence in the CCI. If the price is making new highs, and the CCI is not,
    then a price correction is likely.

    Parameters
    ----------
    data : List[Data]
        The data to use for the CCI calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : PositiveInt, optional
        The length of the CCI, by default 14.
    scalar : PositiveFloat, optional
        The scalar of the CCI, by default 0.015.

    Returns
    -------
    OBBject[List[Data]]
        The CCI data.

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

