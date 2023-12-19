---
title: overview
description: This page provides an API for getting an Alpha Vantage's company overview
  with OpenBB Terminal. It is implemented with Python for stock fundamental analysis.
  A stock's ticker symbol is used as the parameter, and it returns the fundamentals
  in a pd.DataFrame.
keywords:
- Alpha vantage company overview
- OpenBB finance
- OpenBB terminal
- Stocks fundamental analysis
- AV model
- Stock ticker symbol
- Dataframe of fundamentals
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.overview - Reference | OpenBB SDK Docs" />

Get alpha vantage company overview

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/av_model.py#L36)]

```python
openbb.stocks.fa.overview(symbol: str)
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
| pd.DataFrame | Dataframe of fundamentals |
---
