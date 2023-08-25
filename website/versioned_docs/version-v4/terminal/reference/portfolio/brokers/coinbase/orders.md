---
title: orders
description: OpenBB Terminal Function
---

# orders

List your current open orders

### Usage

```python
orders [-l LIMIT] [-s {product_id,side,price,size,type,created_at,status}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit parameter. | 20 | True | None |
| sortby | Sort by given column. Default: created_at | created_at | True | product_id, side, price, size, type, created_at, status |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
