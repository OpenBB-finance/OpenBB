---
title: SIC_SEARCH
description: Learn how to perform a search for industry titles, reporting office,
  and SIC codes using Python. Explore the parameters, returns, and data associated
  with the `obb.regulators.sec.sic_search` function.
keywords: 
- search
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

Search for Industry Titles, Reporting Office, and SIC Codes.

## Syntax

```excel wordwrap
=OBB.REGULATORS.SEC.SIC_SEARCH([query];[provider];[use_cache])
```

### Example

```excel wordwrap
=OBB.REGULATORS.SEC.SIC_SEARCH()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| query | Text | Search query. | False |
| provider | Text | Options: sec, defaults to sec. | False |
| use_cache | Boolean | Whether to use the cache or not. The full list will be cached for seven days if True. (provider: sec) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| sic | Sector Industrial Code (SIC) (provider: sec) |
| industry | Industry title. (provider: sec) |
| office | Reporting office within the Corporate Finance Office (provider: sec) |
