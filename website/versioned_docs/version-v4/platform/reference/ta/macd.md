---
title: macd
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# macd

The Moving Average Convergence Divergence (MACD) is the difference
    between two Exponential Moving Averages. The Signal line is an Exponential Moving
    Average of the MACD.

    The MACD signals trend changes and indicates the start of new trend direction.
    High values indicate overbought conditions, low values indicate oversold conditions.
    Divergence with the price indicates an end to the current trend, especially if the
    MACD is at extreme high or low values. When the MACD line crosses above the
    signal line a buy signal is generated. When the MACD crosses below the signal line a
    sell signal is generated. To confirm the signal, the MACD should be above zero for a buy,
    and below zero for a sell.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    fast : int, optional
        Number of periods for the fast EMA, by default 12.
    slow : int, optional
        Number of periods for the slow EMA, by default 26.
    signal : int, optional
        Number of periods for the signal EMA, by default 9.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> macd_data = obb.ta.macd(data=stock_data.results,target="close",fast=12,slow=26,signal=9)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

