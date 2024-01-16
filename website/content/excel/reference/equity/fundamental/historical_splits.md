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
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_SPLITS(symbol;[provider])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_SPLITS("AAPL")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| provider | Text | Options: fmp, defaults to fmp. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| label | Label of the historical stock splits.  |
| numerator | Numerator of the historical stock splits.  |
| denominator | Denominator of the historical stock splits.  |
