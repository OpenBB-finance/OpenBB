---
title: search
description: OpenBB Terminal Function
---

# search

Search mutual funds in selected country based on selected field.

### Usage

```python
search [-b {name,issuer,isin,symbol}] --fund FUND [FUND ...] [-s {country,name,symbol,issuer,isin,asset_class,currency,underlying}] [-l LIMIT] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| by | Field to search by | name | True | name, issuer, isin, symbol |
| fund | Fund string to search for | None | False | None |
| sortby | Column to sort by | name | True | country, name, symbol, issuer, isin, asset_class, currency, underlying |
| limit | Number of search results to show | 10 | True | None |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
