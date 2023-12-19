---
title: demark
description: Learn how to use the Demark sequential indicator function in the OBBject
  library to analyze stock market data and calculate specific values. See examples
  of its implementation with the OpenBB package.
keywords:
- Demark sequential indicator
- data
- index
- target
- show_all
- asint
- offset
- OBBject
- List[Data]
- calculated data
- examples
- openbb
- equity
- price
- historical
- symbol
- start_date
- provider
- fmp
- technical
- demark
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Demark sequential indicator.

Parameters
----------
data : List[Data]
List of data to be used for the calculation.
index : str, optional
Index column name to use with `data`, by default "date".
target : str, optional
Target column name, by default "close".
show_all : bool, optional
Show 1 - 13. If set to False, show 6 - 9
asint : bool, optional
If True, fill NAs with 0 and change type to int, by default True.
offset : int, optional
How many periods to offset the result

Returns
-------
OBBject[List[Data]]
The calculated data.

Examples
--------
```python
from openbb import obb
stock_data = obb.equity.price.historical(symbol="TSLA", start_date="2023-01-01", provider="fmp")
demark_data = obb.technical.demark(data=stock_data.results,offset=0)
```


---

## Parameters

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

