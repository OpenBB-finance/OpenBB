---
title: aroon
description: This documentation page provides an in-depth overview of the Aroon technical
  indicator within the OpenBBTerminal. It covers the model and chart view of the Aroon
  indicator, with detailed parameters and source code. It also provides the functionality
  to plot the Aroon indicator and export data.
keywords:
- aroon
- technical indicator
- openbb.ta
- openbb.ta.aroon
- openbb.ta.aroon_chart
- trend indicators
- OHLC price data
- plotting
- matplotlib
- axes
- scalar
- window
- symbol
- export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.aroon - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Aroon technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/trend_indicators_model.py#L56)]

```python
openbb.ta.aroon(data: pd.DataFrame, window: int = 25, scalar: int = 100)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe with OHLC price data | None | False |
| window | int | Length of window | 25 | True |
| scalar | int | Scalar variable | 100 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with aroon indicator |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots Aroon indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/trend_indicators_view.py#L121)]

```python
openbb.ta.aroon_chart(data: pd.DataFrame, window: int = 25, scalar: int = 100, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe with OHLC price data | None | False |
| window | int | Length of window | 25 | True |
| symbol | str | Ticker |  | True |
| scalar | int | Scalar variable | 100 | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (3 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
