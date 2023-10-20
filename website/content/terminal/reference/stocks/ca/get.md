---
title: get
description: OpenBB Terminal Function
---

# get

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
