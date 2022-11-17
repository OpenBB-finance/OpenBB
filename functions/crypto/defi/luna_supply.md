---
title: luna_supply
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# luna_supply

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_smartstake_model.get_luna_supply_stats

```python title='openbb_terminal/cryptocurrency/defi/smartstake_model.py'
def get_luna_supply_stats(supply_type: str, days: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/smartstake_model.py#L14)

Description: Get supply history of the Terra ecosystem

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| supply_type | str | Supply type to unpack json | None | False |
| days | int | Day count to fetch data | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of supply history data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_smartstake_view.display_luna_circ_supply_change

```python title='openbb_terminal/decorators.py'
def display_luna_circ_supply_change() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L29)

Description: Display Luna circulating supply stats

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| days | int | Number of days | None | False |
| supply_type | str | Supply type to unpack json | None | False |
| export | str | Export type | None | False |
| limit | int | Number of results display on the terminal
Default: 5 | 5 | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>