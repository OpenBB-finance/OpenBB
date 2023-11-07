---
title: roc
description: This documentation page provides information and implementation details
  about the 'roc' (Rate of Change) function in OpenBB, used to calculate momentum
  oscillations in a given dataset.
keywords:
- roc function
- Rate of Change
- openbb.forecast.roc
- momentum oscillation
- Forecasting
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.roc - Reference | OpenBB SDK Docs" />

A momentum oscillator, which measures the percentage change between the current

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L279)]

```python
openbb.forecast.roc(dataset: pd.DataFrame, target_column: str = "close", period: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to calculate with | None | False |
| target_column | str | The column you wish to add the ROC to | close | True |
| period | int | Time Span | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with added ROC column |
---
