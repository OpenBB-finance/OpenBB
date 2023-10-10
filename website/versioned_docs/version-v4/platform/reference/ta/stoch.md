---
title: stoch
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# stoch

The Stochastic Oscillator measures where the close is in relation
    to the recent trading range. The values range from zero to 100. %D values over 75
    indicate an overbought condition; values under 25 indicate an oversold condition.
    When the Fast %D crosses above the Slow %D, it is a buy signal; when it crosses
    below, it is a sell signal. The Raw %K is generally considered too erratic to use
    for crossover signals.

    Parameters
    ----------
    data : List[Data]
        The data to use for the Stochastic Oscillator calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    fast_k_period : NonNegativeInt, optional
        The fast %K period, by default 14.
    slow_d_period : NonNegativeInt, optional
        The slow %D period, by default 3.
    slow_k_period : NonNegativeInt, optional
        The slow %K period, by default 3.

    Returns
    -------
    OBBject[List[Data]]
        The Stochastic Oscillator data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> stoch_data = obb.ta.stoch(data=stock_data.results, fast_k_period=14, slow_d_period=3, slow_k_period=3)

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

