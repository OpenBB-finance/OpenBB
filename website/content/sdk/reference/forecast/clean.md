---
title: clean
description: The clean function in OpenBB's forecasting toolkit fills or drops NaN
  values on a given dataset, improving data quality.
keywords:
- clean function OpenBB
- forecasting toolkit
- data cleaning
- fill NaN values
- drop NaN values
- dataset
- data quality improvement
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.clean - Reference | OpenBB SDK Docs" />

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
