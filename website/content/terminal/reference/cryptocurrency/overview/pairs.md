---
title: pairs
description: OpenBB Terminal Function
---

# pairs

Shows available trading pairs on Coinbase

### Usage

```python
usage: pairs [-l LIMIT] [-s {id,display_name,base_currency,quote_currency,base_min_size,base_max_size,min_market_funds,max_market_funds}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number of pairs =10 | 15 | True | None |
| sortby | Sort by given column. Default: id | id | True | id, display_name, base_currency, quote_currency, base_min_size, base_max_size, min_market_funds, max_market_funds |
| reverse | Data is sorted in ascending order by default. Reverse flag will sort it in an descending way. Only works when raw data is displayed. | False | True | None |
---

