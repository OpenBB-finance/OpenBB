---
title: ichimoku
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ichimoku

The Ichimoku Cloud, also known as Ichimoku Kinko Hyo, is a versatile indicator that
    defines support and resistance, identifies trend direction, gauges momentum and provides
    trading signals. Ichimoku Kinko Hyo translates into "one look equilibrium chart". With
    one look, chartists can identify the trend and look for potential signals within that trend.

    Parameters
    ----------
    data : List[Data]
        List of data to be used for the calculation.
    index : str, optional
        Index column name to use with `data`, by default "date".
    conversion : PositiveInt, optional
        Number of periods for the conversion line, by default 9.
    base : PositiveInt, optional
        Number of periods for the base line, by default 26.
    lagging : PositiveInt, optional
        Number of periods for the lagging span, by default 52.
    offset : PositiveInt, optional
        Number of periods for the offset, by default 26.
    lookahead : bool, optional
        drops the Chikou Span Column to prevent potential data leak

```python wordwrap

```

---

## Parameters

This function does not take any parameters.

---

## Returns

This function does not return anything

---

