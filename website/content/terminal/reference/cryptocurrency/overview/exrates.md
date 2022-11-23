---
title: exrates
description: OpenBB Terminal Function
---

# exrates

Shows list of crypto, fiats, commodity exchange rates from CoinGecko You can look on only N number of records with --limit, You can sort by Index, Name, Unit, Value, Type, and also use --reverse flag to sort descending.

### Usage

```python
usage: exrates [-l LIMIT] [-s {Index,Name,Unit,Value,Type}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records | 15 | True | None |
| sortby | Sort by given column. Default: Index | Index | True | Index, Name, Unit, Value, Type |
| reverse | Data is sorted in ascending order by default. Reverse flag will sort it in an descending way. Only works when raw data is displayed. | False | True | None |
---

