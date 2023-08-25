---
title: clean
description: OpenBB SDK Function
---

# clean

Clean up NaNs from the dataset

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L100)]

```python
openbb.forecast.clean(dataset: pd.DataFrame, fill: Optional[str] = None, drop: Optional[str] = None, limit: Optional[int] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to clean | None | False |
| fill | Optional[str] | The method of filling NaNs | None | True |
| drop | Optional[str] | The method of dropping NaNs | None | True |
| limit | Optional[int] | The maximum limit you wish to apply that can be forward or backward filled | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with cleaned up data |
---

