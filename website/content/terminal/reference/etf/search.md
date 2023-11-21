---
title: search
description: Learn how to search for ETFs by name using the FinanceDatabase or StockAnalysis.com.
  Understand the usage, parameters, and how to incorporate them in Python.
keywords:
- ETF
- search
- FinanceDatabase
- StockAnalysis
- name
- description
- parameters
- usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf /search - Reference | OpenBB Terminal Docs" />

Search ETF by name [Source: FinanceDatabase/StockAnalysis.com]

### Usage

```python wordwrap
search -n NAME [NAME ...] [-d DESCRIPTION [DESCRIPTION ...]]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| name | -n  --name | Name to look for ETFs |  | False | None |
| description | -d  --description | Name to look for ETFs |  | True | None |

---
