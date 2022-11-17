---
title: team
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# team

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_team

```python title='openbb_terminal/decorators.py'
def get_team() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L411)

Description: Returns coin team

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check team | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | individuals |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_team

```python title='openbb_terminal/decorators.py'
def display_team() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L544)

Description: Display coin team

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check coin team | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>