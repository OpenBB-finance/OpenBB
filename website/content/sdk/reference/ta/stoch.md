---
title: stoch
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# stoch

<Tabs>
<TabItem value="model" label="Model" default>

Stochastic oscillator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L126)]

```python
openbb.ta.stoch(data: pd.DataFrame, fastkperiod: int = 14, slowdperiod: int = 3, slowkperiod: int = 3)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| fastkperiod | int | Fast k period | 14 | True |
| slowdperiod | int | Slow d period | 3 | True |
| slowkperiod | int | Slow k period | 3 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots stochastic oscillator signal

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L307)]

```python
openbb.ta.stoch_chart(data: pd.DataFrame, fastkperiod: int = 14, slowdperiod: int = 3, slowkperiod: int = 3, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| fastkperiod | int | Fast k period | 14 | True |
| slowdperiod | int | Slow d period | 3 | True |
| slowkperiod | int | Slow k period | 3 | True |
| symbol | str | Stock ticker symbol |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (3 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>