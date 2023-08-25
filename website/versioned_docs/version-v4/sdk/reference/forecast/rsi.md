---
title: rsi
description: OpenBB SDK Function
---

# rsi

A momentum indicator that measures the magnitude of recent price changes to evaluate

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L237)]

```python
openbb.forecast.rsi(dataset: pd.DataFrame, target_column: str = "close", period: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to calculate for | None | False |
| target_column | str | The column you wish to add the RSI to | close | True |
| period | int | Time Span | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with added RSI column |
---

