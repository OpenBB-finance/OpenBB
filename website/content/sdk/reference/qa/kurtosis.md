---
title: kurtosis
description: This documentation page provides detailed information about Kurtosis
  Indicator and how to plot rolling kurtosis with OpenBB-finance's tool. It includes
  source code links and parameters needed for these python functions.
keywords:
- OpenBB-finance
- Kurtosis Indicator
- Plotting Kurtosis
- Quantitative Analysis
- Python Functions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.kurtosis - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Kurtosis Indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_model.py#L123)]

```python wordwrap
openbb.qa.kurtosis(data: pd.DataFrame, window: int = 14)
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
| pd.DataFrame | Dataframe of rolling kurtosis |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots rolling kurtosis

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_view.py#L389)]

```python wordwrap
openbb.qa.kurtosis_chart(symbol: str, data: pd.DataFrame, target: str, window: int = 14, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker | None | False |
| data | pd.DataFrame | Dataframe of stock prices | None | False |
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