---
title: gov
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# gov

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_governance

```python title='openbb_terminal/decorators.py'
def get_governance() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L561)

Description: Returns coin governance

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check governance | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| str | governance summary |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_governance

```python title='openbb_terminal/decorators.py'
def display_governance() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L590)

Description: Display coin governance

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check coin governance | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>