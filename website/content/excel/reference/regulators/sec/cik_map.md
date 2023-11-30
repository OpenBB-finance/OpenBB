---
title: cik_map
description: Learn how to retrieve the CIK number corresponding to a ticker symbol
  using the python obb.regulators.sec.cik_map function. Understand the available parameters,
  return values, and data structure.
keywords: 
- CIK number
- ticker symbol
- python obb.regulators.sec.cik_map function
- get data for symbol
- provider parameter
- returns
- results
- warnings
- chart object
- metadata info
- data
- central index key
---

<!-- markdownlint-disable MD041 -->

Get the CIK number corresponding to a ticker symbol.

```excel wordwrap
=OBB.REGULATORS.SEC.CIK_MAP(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: sec | true |

## Data

| Name | Description |
| ---- | ----------- |
| cik | Central Index Key (provider: sec) |
