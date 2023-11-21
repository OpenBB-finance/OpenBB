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

Search mutual funds in selected country

### Usage

```python wordwrap
search --fund FUND [-l LIMIT]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| fund | --fund | Fund string to search for | None | False | None |
| limit | -l  --limit | Number of search results to show | 10 | True | None |

---
