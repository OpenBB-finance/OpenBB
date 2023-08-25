---
title: holders
description: OpenBB Terminal Function
---

# holders

Display top ERC20 token holders: e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 [Source: Ethplorer]

### Usage

```python
holders [-l LIMIT] [-s {balance,share}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: share | share | True | balance, share |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
