---
title: donchian
description: This page provides comprehensive documentation on how to calculate and
  plot Donchian Channels using OpenBB's technical analysis tools. Learn about the
  parameters and return types to leverage this method in your financial modelling
  work.
keywords:
- Donchian Channels
- Technical Analysis
- Financial Modelling
- FinTech
- Volatility Models
- Dataframes
- Data Visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.donchian - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Calculate Donchian Channels

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_model.py#L53)]

```python
openbb.ta.donchian(data: pd.DataFrame, upper_length: int = 20, lower_length: int = 20)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| upper_length | int | Length of window to calculate upper channel | 20 | True |
| lower_length | int | Length of window to calculate lower channel | 20 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of upper and lower channels |
---

</TabItem>
<TabItem value="view" label="Chart">

Plots donchian channels

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volatility_view.py#L112)]

```python
openbb.ta.donchian_chart(data: pd.DataFrame, symbol: str = "", upper_length: int = 20, lower_length: int = 20, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| symbol | str | Ticker symbol |  | True |
| upper_length | int | Length of window to calculate upper channel | 20 | True |
| lower_length | int | Length of window to calculate lower channel | 20 | True |
| export | str | Format of export file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
