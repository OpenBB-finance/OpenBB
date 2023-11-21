---
title: overview
description: This page provides an overview of how to get ETF data using OpenBB's
  Python library. It includes detailed explanations on parameters and returns, and
  even a link to the source code.
keywords:
- ETF
- overview data
- stock overview data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.overview - Reference | OpenBB SDK Docs" />

Get overview data for selected etf

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_model.py#L48)]

```python
openbb.etf.overview(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| etf_symbol | str | Etf symbol to get overview for | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of stock overview data |
---
