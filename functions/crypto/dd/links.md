---
title: links
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# links

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_links

```python title='openbb_terminal/decorators.py'
def get_links() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L186)

Description: Returns asset's links

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check links | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | asset links |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_links

```python title='openbb_terminal/decorators.py'
def display_links() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L237)

Description: Display coin links

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check links | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>