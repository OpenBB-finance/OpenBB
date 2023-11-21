---
title: metrics
description: This page details the process of getting key metrics in stock market
  by using the metrics function with parameters symbol, limit, and quarterly. It includes
  the Python code for this function.
keywords:
- OpenBBTerminal Metrics
- Metrics Function
- Stock Market Metrics
- Python Stock Market Code
- Fundamental Analysis
- FMP model
- Stock ticker symbol
- Quarterly data
- Market Analysis
- Dataframe of Key Metrics
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.metrics - Reference | OpenBB SDK Docs" />

Get key metrics

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L421)]

```python
openbb.stocks.fa.metrics(symbol: str, limit: int = 5, quarterly: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number to get | 5 | True |
| quarterly | bool | Flag to get quarterly data, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of key metrics |
---
