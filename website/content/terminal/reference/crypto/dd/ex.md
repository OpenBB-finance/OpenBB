---
title: ex
description: OpenBB Terminal Function
---

# ex

Get all exchanges found for given coin. You can display only top N number of exchanges with --top parameter. You can sort data by id, name, adjusted_volume_24h_share, fiats --sort parameter and also with --reverse flag to sort ascending. Displays: id, name, adjusted_volume_24h_share, fiats

### Usage

```python
ex [-l LIMIT] [-s {id,name,adjusted_volume_24h_share,fiats}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of records | 10 | True | None |
| sortby | Sort by given column. Default: date | adjusted_volume_24h_share | True | id, name, adjusted_volume_24h_share, fiats |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
