---
title: quantile
description: This page provides documentation and source code for OpenBB's Quantile
  function. It includes info about parameters, return types, and how to generate and
  plot rolling quantile data using Python.
keywords:
- Docusaurus
- Quantile
- Source Code
- Quantitative Analysis
- Plotting Data
- Rolling Quantile
- Python DataFrame
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.quantile - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Overlay Median & Quantile

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_model.py#L72)]

```python wordwrap
openbb.qa.quantile(data: pd.DataFrame, window: int = 14, quantile_pct: float = 0.5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of targeted data | None | False |
| window | int | Length of window | 14 | True |
| quantile_pct | float | Quantile to display | 0.5 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, pd.DataFrame] | Dataframe of rolling median prices over window,<br/>Dataframe of rolling quantile prices over window |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots rolling quantile

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_view.py#L229)]

```python wordwrap
openbb.qa.quantile_chart(data: pd.DataFrame, target: str, symbol: str = "", window: int = 14, quantile: float = 0.5, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
| symbol | str | Stock ticker |  | True |
| window | int | Length of window | 14 | True |
| quantile | float | Quantile to get | 0.5 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>