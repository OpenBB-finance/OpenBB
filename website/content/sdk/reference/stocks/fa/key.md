---
title: key
description: This page provides the source code and explanation on how to get key
  metrics from OpenBB's stocks fundamental analysis. Detailed parameters and return
  value are provided.
keywords:
- key metrics
- stocks
- fundamental analysis
- dataframe
- symbol
- stock ticker
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.key - Reference | OpenBB SDK Docs" />

Get key metrics from overview

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L101)]

```python
openbb.stocks.fa.key(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of key metrics |
---
