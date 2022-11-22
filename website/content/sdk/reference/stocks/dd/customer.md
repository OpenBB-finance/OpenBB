---
title: customer
description: OpenBB SDK Function
---

# customer

Print customers from ticker provided

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/csimarket_model.py#L66)]

```python
openbb.stocks.dd.customer(symbol: str, limit: int = 50)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to select customers from | None | False |
| limit | int | The maximum number of rows to show | 50 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A dataframe of suppliers |
---

