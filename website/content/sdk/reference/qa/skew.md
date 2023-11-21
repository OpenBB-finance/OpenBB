---
title: skew
description: This documentation page provides details on the function openbb.qa.skew,
  used for rolling skewness indicator calculations and plotting. It includes parameters
  description and links to the source code.
keywords:
- Quantitative Analysis
- Skewness Indicator
- Python Coding
- Source Code
- Financial Data Analysis
- Rolling Skew
- Skew Chart
- Parameters
- Window Length
- Stock Ticker
- Data Export
- External Axes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.skew - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Skewness Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_model.py#L103)]

```python wordwrap
openbb.qa.skew(data: pd.DataFrame, window: int = 14)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of targeted data | None | False |
| window | int | Length of window | 14 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of rolling skew |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots rolling skew

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_view.py#L313)]

```python wordwrap
openbb.qa.skew_chart(symbol: str, data: pd.DataFrame, target: str, window: int = 14, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
| window | int | Length of window | 14 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>