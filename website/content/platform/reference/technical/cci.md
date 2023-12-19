---
title: cci
description: Learn about the Commodity Channel Index (CCI) and how it can be used
  to detect market trends, overbought or oversold conditions, and price divergence.
  This documentation provides an overview of the CCI, its parameters, and its calculation,
  along with an explanation of the CCI data it returns.
keywords:
- Commodity Channel Index
- CCI
- market trends
- trading range
- overbought
- oversold
- price divergence
- price correction
- data
- index column
- length
- scalar
- CCI calculation
- CCI data
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Commodity Channel Index (CCI).

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

This function does not take standardized parameters.

---

## Returns

This function does not return a standardized model

---

