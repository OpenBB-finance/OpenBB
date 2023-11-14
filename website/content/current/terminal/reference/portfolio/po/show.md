---
title: show
description: The page provides command usage and parameters for the 'show' feature
  which helps to display selected saved portfolios and its associated categories like
  asset class, country, sector, industry with an option to allocate amount for long
  term investments.
keywords:
- show
- saved portfolios
- usage
- parameters
- portfolios
- categories
- long allocation
- asset class
- country
- sector
- industry
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/po/show - Reference | OpenBB Terminal Docs" />

Show selected saved portfolios

### Usage

```python
show [-pf PORTFOLIOS] [-ct CATEGORIES] [-v LONG_ALLOCATION]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| portfolios | Show selected saved portfolios |  | True | None |
| categories | Show selected categories | ASSET_CLASS, COUNTRY, SECTOR, INDUSTRY | True | None |
| long_allocation | Amount to allocate to portfolio | 1 | True | None |

---
