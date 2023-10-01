---
title: shrs
description: OpenBB SDK Function
---

# shrs

Get shareholders from yahoo

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L75)]

```python
openbb.stocks.fa.shrs(symbol: str, holder: str = "institutional")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| holder | str | Which holder to get table for | institutional | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Major holders |
---

