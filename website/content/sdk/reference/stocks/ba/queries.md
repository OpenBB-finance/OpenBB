---
title: queries
description: Learn how to get related queries from Google API using the `openbb.stocks.ba.queries`
  function in the OpenBB Terminal. This page includes parameters, return types, and
  source code.
keywords:
- OpenBB Terminal
- Google API
- Queries
- Behavioral analysis
- Stock ticker symbol
- Dataframe
- Python
- Source code
- Marketing SEO
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="queries - Ba - Stocks - Reference | OpenBB SDK Docs" />

# queries

Get related queries from google api [Source: google].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_model.py#L73)]

```python
openbb.stocks.ba.queries(symbol: str, limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol to compare | None | False |
| limit | int | Number of queries to show | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of related queries |
---
