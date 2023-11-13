---
title: cg
description: Learn about the Center of Gravity (COG) indicator, how it predicts price
  movements and reversals, and its use in range-bound markets. Explore the parameters,
  examples, and how to calculate COG data with OpenBB for technical analysis.
keywords:
- center of gravity
- COG indicator
- price movements
- price reversals
- oscillators
- range-bound markets
- upcoming price change
- asset trading
- data
- COG calculation
- index column
- length
- COG data
- openbb
- equity price historical
- stock data
- symbol
- start date
- provider
- technical analysis
- TSLA
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Center of Gravity.

The Center of Gravity indicator, in short, is used to anticipate future price movements
and to trade on price reversals as soon as they happen. However, just like other oscillators,
the COG indicator returns the best results in range-bound markets and should be avoided when
the price is trending. Traders who use it will be able to closely speculate the upcoming
price change of the asset.

Parameters
----------
data : List[Data]
The data to use for the COG calculation.
index : str, optional
Index column name to use with `data`, by default "date"
length : PositiveInt, optional
The length of the COG, by default 14

Returns
-------
OBBject[List[Data]]
The COG data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
cg_data = obb.technical.cg(data=stock_data.results, length=14)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

