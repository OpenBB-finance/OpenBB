---
title: mom
description: This page provides information about the momentum oscillator 'mom' function
  in the OpenBB forecast module. It explains the parameters and returns a DataFrame
  with an added MOM column.
keywords:
- momentum oscillator
- mom function
- OpenBB forecast module
- MOM column
- parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.mom - Reference | OpenBB SDK Docs" />

A momentum oscillator, which measures the percentage change between the current

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L308)]

```python
openbb.forecast.mom(dataset: pd.DataFrame, target_column: str = "close", period: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to calculate with | None | False |
| target_column | str | The column you wish to add the MOM to | close | True |
| period | int | Time Span | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with added MOM column |
---
