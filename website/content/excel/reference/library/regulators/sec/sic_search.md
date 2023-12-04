---
title: sic_search
description: Learn how to perform a fuzzy search for industry titles, reporting office,
  and SIC codes using Python. Explore the parameters, returns, and data associated
  with the `obb.regulators.sec.sic_search` function.
keywords: 
- fuzzy search
- industry titles
- reporting office
- SIC codes
- Python
- search query
- provider
- cache
- results
- warnings
- chart
- metadata
- data
- sector industrial code
- industry title
- reporting office
- Corporate Finance Office
---

<!-- markdownlint-disable MD041 -->

Fuzzy search for Industry Titles, Reporting Office, and SIC Codes.

## Syntax

```excel wordwrap
=OBB.REGULATORS.SEC.SIC_SEARCH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: sec | True |
| query | Text | Search query. | True |
| use_cache | Boolean | Whether to use the cache or not. The full list will be cached for seven days if True. (provider: sec) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| sic | Sector Industrial Code (SIC) (provider: sec) |
| industry | Industry title. (provider: sec) |
| office | Reporting office within the Corporate Finance Office (provider: sec) |
