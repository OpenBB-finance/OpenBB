---
title: plot
description: Learn how to harness the power of OpenBB's financial forecasting functions
  such as the plot and plot_chart to visualize data. These Python functions extract
  dataframes and accept options for export format and external plot axes.
keywords:
- plot data visualization
- OpenBB finance
- forecast
- dataframe
- export format
- docusaurus tabs
- optional axes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.plot - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Plot data from a dataset

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L65)]

```python wordwrap
openbb.forecast.plot(data: pd.DataFrame, columns: List[str], export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to plot | None | False |
| columns | List[str] | The columns to show | None | False |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export image |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
<TabItem value="view" label="Chart">

Plot data from a dataset

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L65)]

```python wordwrap
openbb.forecast.plot_chart(data: pd.DataFrame, columns: List[str], export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to plot | None | False |
| columns | List[str] | The columns to show | None | False |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export image |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>