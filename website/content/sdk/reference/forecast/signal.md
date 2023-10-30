---
title: signal
description: This documentation page provides detailed insight on 'signal', a price
  signal based on short/long term price, with instructions on parameters to be entered
  and returns received.
keywords:
- price signal
- short/long term price
- openbb.forecast.signal
- parameters
- returns
- dataframe
- signal column
- dataset
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.signal - Reference | OpenBB SDK Docs" />

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
