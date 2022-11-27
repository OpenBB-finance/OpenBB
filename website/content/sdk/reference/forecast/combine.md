---
title: combine
description: OpenBB SDK Function
---

# combine

Adds the given column of df2 to df1

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L409)]

```python
openbb.forecast.combine(df1: pd.DataFrame, df2: pd.DataFrame, column: str, dataset: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| df1 | pd.DataFrame | The dataframe to add a column to | None | False |
| df2 | pd.DataFrame | The dataframe to lose a column | None | False |
| column | str | The column to transfer | None | False |
| dataset | str | A name for df2 (shows in name of new column) |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The new dataframe |
---

