---
title: sectors
description: Learn about ETF sector weighting using OBB.etf.sectors API. Find information
  about the parameters, returns, and data, including sectors, weights, and exposure
  levels in normalized percentage points.
keywords: 
- ETF Sector weighting
- OBB.etf.sectors
- parameters
- symbol
- provider
- returns
- results
- etf sectors
- warnings
- chart
- metadata
- data
- sector
- weight
- exposure
- normalized percentage points
---

<!-- markdownlint-disable MD041 -->

ETF Sector weighting.

## Syntax

```excel wordwrap
=OBB.ETF.SECTORS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. (ETF) | False |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| sector | Sector of exposure.  |
| weight | Exposure of the ETF to the sector in normalized percentage points.  |
