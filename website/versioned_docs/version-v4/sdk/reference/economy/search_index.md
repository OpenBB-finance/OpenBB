---
title: search_index
description: OpenBB SDK Function
---

# search_index

Search indices by keyword. [Source: FinanceDatabase]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/yfinance_model.py#L725)]

```python
openbb.economy.search_index(keyword: list, limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| keyword | list | The keyword you wish to search for. This can include spaces. | None | False |
| limit | int | The amount of views you want to show, by default this is set to 10. | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Dataframe with the available options. |
---

