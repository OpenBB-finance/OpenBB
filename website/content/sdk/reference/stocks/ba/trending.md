---
title: trending
description: Learn how to obtain trending tickers from Stocktwits using the OpenBB
  Terminal. The page provides clear python code and explanation of the returned dataframe.
  OpenBB Terminal is a powerful tool for financial data analysis.
keywords:
- trending tickers
- stocktwits
- python code
- watchlist count
- financial data analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.trending - Reference | OpenBB SDK Docs" />

Get trending tickers from stocktwits [Source: stocktwits].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/stocktwits_model.py#L79)]

```python
openbb.stocks.ba.trending()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of trending tickers and watchlist count |
---
