---
title: ratios
description: OpenBB SDK Function
---

# ratios

Get key ratios

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L463)]

```python
openbb.stocks.fa.ratios(symbol: str, limit: int = 5, quarterly: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number to get | 5 | True |
| quarterly | bool | Flag to get quarterly data, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of key ratios |
---

