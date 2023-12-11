---
title: institutions_search
description: Learn how to use the OBB.regulators.sec.institutions_search() method
  to look up institutions regulated by the SEC. This method allows you to search for
  institutions based on various parameters such as the query and provider. It returns
  a list of search results and provides additional attributes like warnings, chart,
  and metadata. Explore the attributes like name and cik for more details on the institution.
keywords: 
- institutions regulated by the SEC
- SEC regulated institutions lookup
- SEC regulated institutions search
- SEC institutions search query
- OBB regulator
- InstitutionsSearch class
- provider parameter
- query parameter
- use_cache parameter
- results attribute
- warnings attribute
- chart attribute
- metadata attribute
- name attribute
- cik attribute
---

<!-- markdownlint-disable MD041 -->

Look up institutions regulated by the SEC.

## Syntax

```excel wordwrap
=OBB.REGULATORS.SEC.INSTITUTIONS_SEARCH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: sec | True |
| query | Text | Search query. | True |
| use_cache | Boolean | Whether or not to use cache. If True, cache will store for seven days. (provider: sec) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| name | The name of the institution. (provider: sec) |
| cik | Central Index Key (CIK) (provider: sec) |
