---
title: ex
description: An in-depth guide to using the 'ex' command to retrieve and manipulate
  data from various crypto exchanges. Learn how to limit query results, sort data
  by important parameters such as id and volume, and switch between ascending and
  descending order.
keywords:
- exchanges
- coin
- crypto
- parameters
- sorted data
- ascend
- descend
- limit
- fiats
- id
- name
- adjusted_volume_24h_share
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/dd/ex - Reference | OpenBB Terminal Docs" />

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
