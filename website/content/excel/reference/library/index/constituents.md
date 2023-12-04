---
title: constituents
description: Learn how to fetch constituents of an index using the OBB library in
  Python. Get detailed information such as symbol, name, sector, sub-sector, headquarters,
  date of first addition, CIK, and founding year of the constituent companies in the
  index.
keywords: 
- index constituents
- fetch constituents
- index constituents parameters
- index constituents returns
- index constituents data
- index constituents symbol
- index constituents name
- index constituents sector
- index constituents sub-sector
- index constituents headquarters
- index constituents date first added
- index constituents cik
- index constituents founding year
---

<!-- markdownlint-disable MD041 -->

Index Constituents. Constituents of an index.

## Syntax

```excel wordwrap
=OBB.INDEX.CONSTITUENTS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp | True |
| index | Text | Index for which we want to fetch the constituents. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the constituent company in the index.  |
| sector | Sector the constituent company in the index belongs to.  |
| sub_sector | Sub-sector the constituent company in the index belongs to.  |
| headquarter | Location of the headquarter of the constituent company in the index.  |
| date_first_added | Date the constituent company was added to the index.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| founded | Founding year of the constituent company in the index.  |
