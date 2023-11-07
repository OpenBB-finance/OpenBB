---
title: dupont
description: This page provides source code for the function openbb.stocks.fa.dupont
  that returns the dupont ratio breakdown for a given stock ticker symbol.
keywords:
- dupont ratios
- Stock ticker symbol
- openbb.stocks.fa.dupont
- dupont ratio breakdown
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.dupont - Reference | OpenBB SDK Docs" />

Get dupont ratios

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L715)]

```python
openbb.stocks.fa.dupont(symbol: str)
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
| pd.DataFrame | The dupont ratio breakdown |
---
