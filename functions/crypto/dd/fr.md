---
title: fr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fr

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_fundraising

```python title='openbb_terminal/decorators.py'
def get_fundraising() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L632)

Description: Returns coin fundraising

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check fundraising | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| str | launch summary |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_fundraising

```python title='openbb_terminal/decorators.py'
def display_fundraising() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L627)

Description: Display coin fundraising

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check coin fundraising | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>