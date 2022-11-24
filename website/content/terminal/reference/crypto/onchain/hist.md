---
title: hist
description: OpenBB Terminal Function
---

# hist

Display history for given ethereum blockchain balance. e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699 [Source: Ethplorer]

### Usage

```python
hist [-l LIMIT] [-s {timestamp,transactionHash,token,value}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: timestamp | timestamp | True | timestamp, transactionHash, token, value |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
