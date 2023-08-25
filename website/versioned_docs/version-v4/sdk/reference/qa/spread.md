---
title: spread
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# spread

<Tabs>
<TabItem value="model" label="Model" default>

Standard Deviation and Variance

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_model.py#L41)]

```python
openbb.qa.spread(data: pd.DataFrame, window: int = 14)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame of targeted data | None | False |
| window | int | Length of window | 14 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame] | Dataframe of rolling standard deviation,<br/>Dataframe of rolling variance |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots rolling spread

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_view.py#L135)]

```python
openbb.qa.spread_chart(data: pd.DataFrame, target: str, symbol: str = "", window: int = 14, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
| target | str | Column in data to look at | None | False |
| symbol | str | Stock ticker |  | True |
| window | int | Length of window | 14 | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (3 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>