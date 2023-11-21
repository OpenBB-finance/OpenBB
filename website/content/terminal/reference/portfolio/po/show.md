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

<HeadTitle title="portfolio /po/show - Reference | OpenBB Terminal Docs" />

Show selected saved portfolios

### Usage

```python wordwrap
show [-pf PORTFOLIOS] [-ct CATEGORIES] [-v LONG_ALLOCATION]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| portfolios | -pf  --portfolios | Show selected saved portfolios |  | True | None |
| categories | -ct  --categories | Show selected categories |  | True | None |
| long_allocation | -v  --value | Amount to allocate to portfolio | 1 | True | None |

---
