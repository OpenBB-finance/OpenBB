---
title: options
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# options

<Tabs>
<TabItem value="model" label="Model" default>

## econometrics_model.get_options

```python title='openbb_terminal/econometrics/econometrics_model.py'
def get_options(datasets: Dict[str, pd.DataFrame], dataset_name: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L21)

Description: Obtain columns-dataset combinations from loaded in datasets that can be used in other commands

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| datasets | dict | The available datasets. | None | False |
| dataset_name | str | The dataset you wish to show the options for. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| dict | A dictionary with a DataFrame for each option. With dataset_name set, only shows one
options table. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## econometrics_view.show_options

```python title='openbb_terminal/econometrics/econometrics_view.py'
def show_options(datasets: Dict[str, pd.DataFrame], dataset_name: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L34)

Description: Plot custom data

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| datasets | dict | The loaded in datasets | None | False |
| dataset_name | str | The name of the dataset you wish to show options for | None | False |
| export | str | Format to export image | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>