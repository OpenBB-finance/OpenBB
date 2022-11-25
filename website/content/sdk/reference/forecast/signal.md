---
title: signal
description: OpenBB SDK Function
---

# signal

A price signal based on short/long term price.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L374)]

```python
openbb.forecast.signal(dataset: pd.DataFrame, target_column: str = "close")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to calculate with | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with added signal column |
---

