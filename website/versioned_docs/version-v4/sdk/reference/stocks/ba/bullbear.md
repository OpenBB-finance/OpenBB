---
title: bullbear
description: OpenBB SDK Function
---

# bullbear

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

