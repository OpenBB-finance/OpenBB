---
title: options
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# options

<Tabs>
<TabItem value="model" label="Model" default>

Obtain columns-dataset combinations from loaded in datasets that can be used in other commands

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L23)]

```python
openbb.econometrics.options(datasets: Dict[str, pd.DataFrame], dataset_name: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| datasets | dict | The available datasets. | None | False |
| dataset_name | str | The dataset you wish to show the options for. |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[Union[str, Any], pd.DataFrame] | A dictionary with a DataFrame for each option. With dataset_name set, only shows one<br/>options table. |
---



</TabItem>
<TabItem value="view" label="Chart">

Plot custom data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L27)]

```python
openbb.econometrics.options_chart(datasets: Dict[str, pd.DataFrame], dataset_name: str = None, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| datasets | dict | The loaded in datasets | None | False |
| dataset_name | str | The name of the dataset you wish to show options for | None | True |
| export | str | Format to export image |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>