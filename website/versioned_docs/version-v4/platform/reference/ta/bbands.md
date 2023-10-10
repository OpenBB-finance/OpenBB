---
title: bbands
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# bbands

Bollinger Bands consist of three lines. The middle band is a simple
    moving average (generally 20 periods) of the typical price (TP). The upper and lower
    bands are F standard deviations (generally 2) above and below the middle band.
    The bands widen and narrow when the volatility of the price is higher or lower,
    respectively.

    Bollinger Bands do not, in themselves, generate buy or sell signals;
    they are an indicator of overbought or oversold conditions. When the price is near the
    upper or lower band it indicates that a reversal may be imminent. The middle band
    becomes a support or resistance level. The upper and lower bands can also be
    interpreted as price targets. When the price bounces off of the lower band and crosses
    the middle band, then the upper band becomes the price target.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    target : str
        Target column name.
    index : str, optional
        Index column name to use with `data`, by default "date".
    length : int, optional
        Number of periods to be used for the calculation, by default 50.
    std : NonNegativeFloat, optional
        Standard deviation to be used for the calculation, by default 2.
    mamode : Literal["sma", "ema", "wma", "rma"], optional
        Moving average mode to be used for the calculation, by default "sma".
    offset : int, optional
        Offset to be used for the calculation, by default 0.

    Returns
    -------
    OBBject[List[Data]]
        The calculated data.

    Examples
    --------
    >>> from openbb import obb
    >>> stock_data = obb.stocks.load(symbol="TSLA", start_date="2023-01-01", provider="fmp")
    >>> bbands = obb.ta.bbands(
    >>>     data=stock_data.results, target="close", length=50, std=2, mamode="sma", offset=0
    >>> )

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

