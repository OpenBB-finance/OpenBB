---
title: rm
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rm

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_roadmap

```python title='openbb_terminal/decorators.py'
def get_roadmap() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L225)

Description: Returns coin roadmap

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check roadmap | None | False |
| ascend | bool | reverse order | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | roadmap |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_roadmap

```python title='openbb_terminal/decorators.py'
def display_roadmap() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L272)

Description: Display coin roadmap

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check roadmap | None | False |
| ascend | bool | reverse order | None | False |
| limit | int | number to show | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>