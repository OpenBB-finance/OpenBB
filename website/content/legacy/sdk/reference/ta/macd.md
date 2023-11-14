---
title: macd
description: This page provides a comprehensive guide to MACD (Moving Average Convergence
  Divergence) implementation in OpenBB terminal. It explains how to model and visualize
  the MACD signal using Python as well as the parameters involved.
keywords:
- macd
- OpenBB_terminal
- technical analysis
- moving average convergence divergence
- plotting macd
- macd signal
- data visualization
- momentum model
- momentum view
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.macd - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Moving average convergence divergence

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L61)]

```python
openbb.ta.macd(data: pd.Series, n_fast: int = 12, n_slow: int = 26, n_signal: int = 9)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Values for calculation | None | False |
| n_fast | int | Fast period | 12 | True |
| n_slow | int | Slow period | 26 | True |
| n_signal | int | Signal period | 9 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of technical indicator |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots MACD signal

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L126)]

```python
openbb.ta.macd_chart(data: pd.Series, n_fast: int = 12, n_slow: int = 26, n_signal: int = 9, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Values to input | None | False |
| n_fast | int | Fast period | 12 | True |
| n_slow | int | Slow period | 26 | True |
| n_signal | int | Signal period | 9 | True |
| symbol | str | Stock ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
