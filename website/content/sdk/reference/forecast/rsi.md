---
title: rsi
description: This document provides detailed information about the RSI (Relative Strength
  Index) function in OpenBB.finance, including how to use this momentum indicator
  to measure recent price changes. The function uses a Pandas DataFrame to calculate
  the RSI and add it back to your dataset. The page also links to the function's source
  code.
keywords:
- RSI
- momentum indicator
- price changes
- OpenBB.finance
- forecast
- Pandas DataFrame
- RSI calculation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.rsi - Reference | OpenBB SDK Docs" />

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
