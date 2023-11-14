---
title: sto
description: Page about the Stochastic Oscillator (STO) function in the OpenBB library.
  It includes information about calculating momentum indicators, source code, parameters,
  and what it returns.
keywords:
- sto
- stochastic oscillator
- momentum indicator
- forecasting
- k & d columns
- dataset
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.sto - Reference | OpenBB SDK Docs" />

Stochastic Oscillator %K and %D : A stochastic oscillator is a momentum indicator comparing a particular closing

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L187)]

```python
openbb.forecast.sto(dataset: pd.DataFrame, close_column: str = "close", high_column: str = "high", low_column: str = "low", period: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to calculate for | None | False |
| period | int | Span | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with added STO K & D columns |
---
