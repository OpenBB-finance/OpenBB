---
title: rise
description: Discover top rising related queries for a stock's symbol with the OpenBB
  rise tool. Analyze market behavior and spot trends.
keywords:
- stock analysis
- market trends
- rising queries
- stock symbol use
- OpenBB rise tool
- behavioral analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.rise - Reference | OpenBB SDK Docs" />

Get top rising related queries with this stock's query [Source: google].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_model.py#L106)]

```python
openbb.stocks.ba.rise(symbol: str, limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of queries to show | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing rising related queries |
---
