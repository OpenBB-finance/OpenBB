---
title: ad
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ad

<Tabs>
<TabItem value="model" label="Model" default>

Calculate AD technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_model.py#L17)]

```python
openbb.ta.ad(data: pd.DataFrame, use_open: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of prices with OHLC and Volume | None | False |
| use_open | bool | Whether to use open prices | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots AD technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/volume_view.py#L28)]

```python
openbb.ta.ad_chart(data: pd.DataFrame, use_open: bool = False, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of ohlc prices | None | False |
| use_open | bool | Whether to use open prices in calculation | False | True |
| symbol | str | Ticker symbol |  | True |
| export | str | Format to export data as |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (3 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>