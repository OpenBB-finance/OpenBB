---
title: cnews
description: OpenBB SDK Function
---

# cnews

Get news from a company. [Source: Finnhub]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/behavioural_analysis/finnhub_model.py#L20)]

```python
openbb.stocks.ba.cnews(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | company ticker to look for news articles | None | False |
| start_date | Optional[str] | date to start searching articles, with format YYYY-MM-DD | None | True |
| end_date | Optional[str] | date to end searching articles, with format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| List | term to search on the news articles |
---

