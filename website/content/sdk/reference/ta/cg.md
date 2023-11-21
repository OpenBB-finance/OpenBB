---
title: cg
description: Documentation for Center of Gravity Indicator function 'cg' and its graphical
  representation 'cg_chart' in the OpenBB Terminal. Explanation of their source code,
  parameters, and returns are covered.
keywords:
- Center of Gravity Indicator
- Technical Analysis
- Source Code
- Parameters
- Returns
- Charts
- pd.Series
- matplotlib
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.cg - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Center of gravity

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L189)]

```python wordwrap
openbb.ta.cg(values: pd.Series, window: int)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| values | pd.DataFrame | Data to use with close being titled values | None | False |
| window | int | Length for indicator window | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of technical indicator |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots center of gravity Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L275)]

```python wordwrap
openbb.ta.cg_chart(data: pd.Series, window: int = 14, symbol: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of values | None | False |
| window | int | Length of window | 14 | True |
| symbol | str | Stock ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>