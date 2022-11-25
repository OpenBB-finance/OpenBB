---
title: whales
description: OpenBB Terminal Function
---

# whales

Display crypto whales transactions. [Source: https://docs.whale-alert.io/]

### Usage

```python
whales [-m MIN] [-l LIMIT] [-s {date,symbol,blockchain,amount,amount_usd,from,to}] [-r] [-a]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| min | Minimum value of transactions. | 1000000 | True | None |
| limit | display N number records | 10 | True | None |
| sortby | Sort by given column. Default: date | date | True | date, symbol, blockchain, amount, amount_usd, from, to |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| address | Flag to show addresses of transaction | False | True | None |

---
