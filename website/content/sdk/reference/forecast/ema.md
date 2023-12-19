---
title: ema
description: Documentation on how to use the EMA (Exponential Moving Average) function
  with OpenBB Terminal. The function receives a dataset and returns a DataFrame with
  an added EMA column, providing an indication of price trend movement.
keywords:
- EMA
- Moving average
- Price trend
- Forecast
- Dataset
- Source code
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.ema - Reference | OpenBB SDK Docs" />

A moving average provides an indication of the trend of the price movement

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L159)]

```python
openbb.forecast.ema(dataset: pd.DataFrame, target_column: str = "close", period: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to clean | None | False |
| target_column | str | The column you wish to add the EMA to | close | True |
| period | int | Time Span | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with added EMA column |
---
