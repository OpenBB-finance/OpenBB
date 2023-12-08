---
title: available
description: Available Indices
keywords: 
- index
- available
---

<!-- markdownlint-disable MD041 -->

Available Indices. Available indices for a given provider.

## Syntax

```excel wordwrap
=OBB.INDEX.AVAILABLE(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| name | Name of the index.  |
| currency | Currency the index is traded in.  |
| stock_exchange | Stock exchange where the index is listed. (provider: fmp) |
| exchange_short_name | Short name of the stock exchange where the index is listed. (provider: fmp) |
