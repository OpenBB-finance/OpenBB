---
title: pi
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pi

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_project_product_info

```python title='openbb_terminal/decorators.py'
def get_project_product_info() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L342)

Description: Returns coin product info

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check product info | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Metric, Value with project and technology details |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_project_info

```python title='openbb_terminal/decorators.py'
def display_project_info() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L458)

Description: Display project info

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check project info | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>