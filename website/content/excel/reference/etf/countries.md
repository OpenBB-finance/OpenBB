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

```jsx<span style={color: 'red'}>=OBB.ETF.COUNTRIES(symbol;[provider])</span>```

### Example

```excel wordwrap
=OBB.ETF.COUNTRIES("SPY")
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for. (ETF)** | **False** |
| provider | Text | Options: fmp, defaults to fmp. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| country | The country of the exposure.  Corresponding values are normalized percentage points.  |
