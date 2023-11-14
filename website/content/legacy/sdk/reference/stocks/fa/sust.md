---
title: sust
description: This page provides information on how to get sustainability metrics for
  a stock, using the OpenBB platform which relies on Yahoo Finance. It includes necessary
  parameters and return values.
keywords:
- sustainability metrics
- Yahoo Finance
- stock
- ticker symbol
- dataframe
- fundamental analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.sust - Reference | OpenBB SDK Docs" />

Get sustainability metrics from yahoo

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L138)]

```python
openbb.stocks.fa.sust(symbol: str)
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
| pd.DataFrame | Dataframe of sustainability metrics |
---
