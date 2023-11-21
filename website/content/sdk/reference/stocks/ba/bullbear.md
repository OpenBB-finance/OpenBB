---
title: bullbear
description: This page provides information on how to use OpenBB's bullbear function
  that fetches sentiment for a ticker from stocktwits. Detailed info about parameters
  and returns are included.
keywords:
- bullbear function
- stocktwits
- sentiment analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.bullbear - Reference | OpenBB SDK Docs" />

Gets bullbear sentiment for ticker [Source: stocktwits].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/stocktwits_model.py#L16)]

```python
openbb.stocks.ba.bullbear(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to look at | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[int, int, int, int] | Watchlist count,<br/>Number of cases found for ticker,<br/>Number of bullish statements,<br/>Number of bearish statements, |
---
