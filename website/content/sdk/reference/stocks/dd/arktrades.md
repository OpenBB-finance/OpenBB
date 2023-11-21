---
title: arktrades
description: Arktrades is a feature provided by OpenBB Stocks, a function in Python
  facilitating due diligence for stock trading. This page contains the guide to access
  ARK trades for a particular stock ticker, returning a dataframe of trades. Source
  code included, hosted on GitHub.
keywords:
- arktrades
- OpenBB Stocks
- Stocks Due Diligence
- trade dataframe
- ARK trades
- Stock Ticker
- Stock Trades
- GitHub Source Code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dd.arktrades - Reference | OpenBB SDK Docs" />

Gets a dataframe of ARK trades for ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/ark_model.py#L19)]

```python
openbb.stocks.dd.arktrades(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get trades for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of trades |
---
