---
title: balance
description: OpenBB Terminal Function
---

# balance

Display info about tokens on given ethereum blockchain balance. [Source: Ethplorer]

### Usage

```python
balance [-l LIMIT] [-s {index,balance,tokenName,tokenSymbol}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: index | index | True | index, balance, tokenName, tokenSymbol |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
