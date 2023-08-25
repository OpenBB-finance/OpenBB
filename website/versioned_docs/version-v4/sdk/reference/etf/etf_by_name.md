---
title: etf_by_name
description: OpenBB SDK Function
---

# etf_by_name

Get an ETF symbol and name based on ETF string to search. [Source: StockAnalysis]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_model.py#L132)]

```python
openbb.etf.etf_by_name(name_to_search: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name_to_search | str | ETF name to match | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Dataframe with symbols and names |
---

