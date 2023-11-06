---
title: get
description: A document page explaining the usage of the 'get' command in python.
  It allows users to fetch similar companies from a data source for comparison. Instructions
  and parameters for limiting the stocks and filtering by U.S. stock exchanges, Industry
  and Sector are also included.
keywords:
- get
- similar companies
- data source
- Finviz
- parameters
- Polygon
- stocks
- US stock exchanges
- Industry
- Sector
- limit
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ca/get - Reference | OpenBB Terminal Docs" />

Get similar companies from selected data source (default: Finviz) to compare with.

### Usage

```python
get [-u] [-n] [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| us_only | Show only stocks from the US stock exchanges. Works only with Polygon | False | True | None |
| b_no_country | Similar stocks from finviz using only Industry and Sector. | False | True | None |
| limit | Limit of stocks to retrieve. | 10 | True | None |

---
