---
title: sbc
description: This documentation page describes how to use the sbc or 'search by category'
  feature on FinanceDatabase/StockAnalysis.com. It provides detailed information about
  parameters for category and limit. It specifically caters to ETFs data lookup.
keywords:
- sbc
- search by category
- FinanceDatabase
- StockAnalysis.com
- usage
- parameters
- category
- limit
- ETFs
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/screener/sbc - Reference | OpenBB Terminal Docs" />

Search by category [Source: FinanceDatabase/StockAnalysis.com]

### Usage

```python
sbc -c CATEGORY [CATEGORY ...] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| category | Category to look for | None | False | None |
| limit | Limit of ETFs to display | 5 | True | None |

---
