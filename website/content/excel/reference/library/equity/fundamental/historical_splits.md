---
title: historical_splits
description: Learn how to retrieve historical stock splits data using the Python obb.equity.fundamental.historical_splits
  function. Understand the parameters, returns, and data structure for this API call.
keywords: 
- historical stock splits
- stock splits data
- python obb.equity.fundamental.historical_splits
- parameters
- symbol
- provider
- returns
- results
- provider name
- warnings
- chart object
- metadata
- data
- date
- label
- numerator
- denominator
---

<!-- markdownlint-disable MD041 -->

Historical Splits. Historical splits data.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_SPLITS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| label | Label of the historical stock splits.  |
| numerator | Numerator of the historical stock splits.  |
| denominator | Denominator of the historical stock splits.  |
