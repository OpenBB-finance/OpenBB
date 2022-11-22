---
title: balance
description: OpenBB SDK Function
---

# balance

Get balance data. [Source: Marketwatch].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/marketwatch_model.py#L107)]

```python
openbb.stocks.ca.balance(similar: List[str], timeframe: str = "2021", quarter: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of tickers to compare.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| timeframe | str | Column header to compare | 2021 | True |
| quarter | bool | Whether to use quarterly statements, by default False | False | True |
| export | str | Format to export data | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of balance comparisons |
---

