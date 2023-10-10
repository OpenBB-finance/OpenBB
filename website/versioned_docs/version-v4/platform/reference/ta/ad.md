---
title: ad
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ad

The Accumulation/Distribution Line is similar to the On Balance
    Volume (OBV), which sums the volume times +1/-1 based on whether the close is
    higher than the previous close. The Accumulation/Distribution indicator, however
    multiplies the volume by the close location value (CLV). The CLV is based on the
    movement of the issue within a single bar and can be +1, -1 or zero.


    The Accumulation/Distribution Line is interpreted by looking for a divergence in
    the direction of the indicator relative to price. If the Accumulation/Distribution
    Line is trending upward it indicates that the price may follow. Also, if the
    Accumulation/Distribution Line becomes flat while the price is still rising (or falling)
    then it signals an impending flattening of the price.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    offset : int, optional
        Offset of the AD, by default 0.

    Returns
    -------
    OBBject[List[Data]]

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> ad_data = obb.ta.ad(data=stock_data.results,offset=0)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

