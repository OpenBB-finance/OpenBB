---
title: top
description: OpenBB Terminal Function
---

# top

Display top ERC20 tokens. [Source: Ethplorer]

### Usage

```python
usage: top [-l LIMIT] [-s {rank,name,symbol,price,txsCount,transfersCount,holdersCount}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: rank | rank | True | rank, name, symbol, price, txsCount, transfersCount, holdersCount |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

