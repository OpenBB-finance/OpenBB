---
title: cci
description: This page provides information on the Commodity Channel Index (CCI) utility
  as part of the OpenBB platform. It comprises details about the technical model,
  related parameters, expected returns, and source code linked to Github. Also includes
  instructions for plotting CCI Indicator.
keywords:
- CCI
- Commodity channel index
- technical indicator
- dataframe
- Source code
- Parameters
- Returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.cci - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Commodity channel index

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L20)]

```python
openbb.ta.cci(data: pd.DataFrame, window: int = 14, scalar: float = 0.0015)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| high_vals | pd.Series | High values | None | True |
| low_values | pd.Series | Low values | None | True |
| close-values | pd.Series | Close values | None | True |
| window | int | Length of window | 14 | True |
| scalar | float | Scalar variable | 0.0015 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of technical indicator |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots CCI Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L34)]

```python
openbb.ta.cci_chart(data: pd.DataFrame, window: int = 14, scalar: float = 0.0015, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC | None | False |
| window | int | Length of window | 14 | True |
| scalar | float | Scalar variable | 0.0015 | True |
| symbol | str | Stock ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
