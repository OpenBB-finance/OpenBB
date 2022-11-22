---
title: screener
description: OpenBB SDK Function
---

# screener

Screener Overview.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/finviz_compare_model.py#L53)]

```python
openbb.stocks.ca.screener(similar: List[str], data_type: str = "overview")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar |  | List of similar companies.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| data_type | str | Data type between: overview, valuation, financial, ownership, performance, technical | overview | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with overview, valuation, financial, ownership, performance or technical |
---

