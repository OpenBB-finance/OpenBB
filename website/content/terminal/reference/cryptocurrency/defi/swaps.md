---
title: swaps
description: OpenBB Terminal Function
---

# swaps

Display last swaps done on Uniswap DEX. [Source: https://thegraph.com/en/]

### Usage

```python
usage: pairs [-l LIMIT] [-s {Datetime,USD,From,To}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Number of records to display | 10 | True | None |
| sortby | Sort by given column. Default: timestamp | Datetime | True | Datetime, USD, From, To |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

