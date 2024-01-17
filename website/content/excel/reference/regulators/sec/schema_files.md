---
title: SCHEMA_FILES
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

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="REGULATORS.SEC.SCHEMA_FILES | OpenBB Add-in for Excel Docs" />

Get lists of SEC XML schema files by year.

## Syntax

```excel wordwrap
=OBB.REGULATORS.SEC.SCHEMA_FILES([query];[provider];[url])
```

### Example

```excel wordwrap
=OBB.REGULATORS.SEC.SCHEMA_FILES()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| query | Text | Search query. | False |
| provider | Text | Options: sec, defaults to sec. | False |
| url | Text | Enter an optional URL path to fetch the next level. (provider: sec) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| files | Dictionary of URLs to SEC Schema Files (provider: sec) |
