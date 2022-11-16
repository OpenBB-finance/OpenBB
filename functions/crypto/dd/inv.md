---
title: inv
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# inv

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_investors

```python title='openbb_terminal/decorators.py'
def get_investors() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L487)

Description: Returns coin investors

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check investors | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | individuals |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_investors

```python title='openbb_terminal/decorators.py'
def display_investors() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L498)

Description: Display coin investors

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check coin investors | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>