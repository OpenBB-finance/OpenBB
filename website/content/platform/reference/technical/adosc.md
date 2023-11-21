---
title: adosc
description: Learn about the Accumulation/Distribution Oscillator, also known as the
  Chaikin Oscillator. This momentum indicator examines the strength of price moves
  and underlying buying and selling pressure. Discover how divergence between the
  indicator and price signals market turning points. Explore the parameters, data,
  and examples for using this oscillator in your analysis.
keywords:
- Accumulation/Distribution Oscillator
- Chaikin Oscillator
- momentum indicator
- Accumulation-Distribution line
- buying pressure
- selling pressure
- divergence
- market turning points
- parameters
- data
- fast calculation
- slow calculation
- offset
- returns
- examples
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Accumulation/Distribution Oscillator.

Also known as the Chaikin Oscillator.

Essentially a momentum indicator, but of the Accumulation-Distribution line
rather than merely price. It looks at both the strength of price moves and the
underlying buying and selling pressure during a given time period. The oscillator
reading above zero indicates net buying pressure, while one below zero registers
net selling pressure. Divergence between the indicator and pure price moves are
the most common signals from the indicator, and often flag market turning points.

Parameters
----------
data : List[Data]
List of data to be used for the calculation.
fast : PositiveInt, optional
Number of periods to be used for the fast calculation, by default 3.
slow : PositiveInt, optional
Number of periods to be used for the slow calculation, by default 10.
offset : int, optional
Offset to be used for the calculation, by default 0.

Returns
-------
OBBject[List[Data]]

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
adosc_data = obb.technical.adosc(data=stock_data.results, fast=3, slow=10, offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

