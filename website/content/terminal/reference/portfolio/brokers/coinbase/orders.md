---
title: orders
description: The page explains how open orders can be listed. It provides information
  on usage and parameters such as limit, sortby, and reverse.
keywords:
- orders
- open orders
- parameters
- limit
- sortby
- reverse
- descending order
- ascending order
- raw data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /brokers/coinbase/orders - Reference | OpenBB Terminal Docs" />

List your current open orders

### Usage

```python wordwrap
orders [-l LIMIT] [-s {product_id,side,price,size,type,created_at,status}] [-r]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| limit | -l  --limit | Limit parameter. | 20 | True | None |
| sortby | -s  --sort | Sort by given column. Default: created_at | created_at | True | product_id, side, price, size, type, created_at, status |
| reverse | -r  --reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
