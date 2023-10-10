---
title: fisher
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fisher

The Fisher Transform is a technical indicator created by John F. Ehlers
    that converts prices into a Gaussian normal distribution.1 The indicator
    highlights when prices have   moved to an extreme, based on recent prices.
    This may help in spotting turning points in the price of an asset. It also
    helps show the trend and isolate the price waves within a trend.

    Parameters
    ----------
    data : List[Data]
        List of data to apply the indicator to.
    index : str, optional
        Index column name, by default "date"
    length : PositiveInt, optional
        Fisher period, by default 14
    signal : PositiveInt, optional
        Fisher Signal period, by default 1

    Returns
    -------
    OBBject[List[Data]]
        List of data with the indicator applied.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> fisher_data = obb.ta.fisher(data=stock_data.results, length=14, signal=1)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

