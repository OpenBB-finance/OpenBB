---
title: rename
description: OpenBB SDK Function
---

# rename

Rename a column in a dataframe

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L477)]

```python
openbb.forecast.rename(data: pd.DataFrame, old_column: str, new_column: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to have a column renamed | None | False |
| old_column | str | The column that will have its name changed | None | False |
| new_column | str | The name to update to | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The dataframe with the renamed column |
---

