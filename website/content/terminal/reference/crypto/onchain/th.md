---
title: th
description: OpenBB Terminal Function
---

# th

Displays info about token history. e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 [Source: Ethplorer]

### Usage

```python
th [-l LIMIT] [-s {value}] [-r] [--hash]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: value | value | True | value |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| hash | Flag to show transaction hash | True | True | None |

---
