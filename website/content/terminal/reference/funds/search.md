---
title: search
description: This page provides search features for mutual funds in a selected country
  based on various selectable fields. It incorporates features of result sorting and
  limiting, displayed in either ascending or descending order.
keywords:
- Search
- Mutual Funds
- Country
- Fields
- Fund Info
- Data Sorting
- Results Limit
- Ascending Order
- Descending Order
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds /search - Reference | OpenBB Terminal Docs" />

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
