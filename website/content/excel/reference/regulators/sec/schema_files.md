---
title: schema_files
description: Get lists of SEC XML schema files by year with the OBBect function. Returns
  serializable results, provider name, warnings list, chart object, metadata info,
  and data including a list of URLs to SEC Schema Files.
keywords: 
- SEC XML schema files
- SEC XML schema files by year
- get SEC XML schema files
- OBBect
- Serializable results
- provider name
- warnings list
- chart object
- metadata info
- fetch URL path
- data
- list of URLs to SEC Schema Files
---

<!-- markdownlint-disable MD041 -->

Get lists of SEC XML schema files by year.

```excel wordwrap
=OBB.REGULATORS.SEC.SCHEMA_FILES(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: sec | true |
| query | string | Search query. | true |
| url | string | Enter an optional URL path to fetch the next level. (provider: sec) | true |

## Data

| Name | Description |
| ---- | ----------- |
| files | Dictionary of URLs to SEC Schema Files (provider: sec) |
