---
title: countries
description: Learn about ETF country weighting and how to retrieve country exposure
  data using obb.etf.countries API endpoint.
keywords: 
- ETF country weighting
- obb.etf.countries
- symbol
- provider
- etf
- data
- results
- chart
- metadata
- country exposure
---

<!-- markdownlint-disable MD041 -->

ETF Country weighting.

## Syntax

```excel wordwrap
=OBB.ETF.COUNTRIES(symbol;[provider])
```

### Example

```excel wordwrap
=OBB.ETF.COUNTRIES("SPY")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for. (ETF)** | **True** |
| provider | Text | Options: fmp, defaults to fmp. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| country | The country of the exposure.  Corresponding values are normalized percentage points.  |
