---
title: ayr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ayr

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_terraengineer_model.get_anchor_yield_reserve

```python title='openbb_terminal/cryptocurrency/defi/terraengineer_model.py'
def get_anchor_yield_reserve() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terraengineer_model.py#L62)

Description: Displays the 30-day history of the Anchor Yield Reserve.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing historical data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_terraengineer_view.display_anchor_yield_reserve

```python title='openbb_terminal/cryptocurrency/defi/terraengineer_view.py'
def display_anchor_yield_reserve(export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terraengineer_view.py#L85)

Description: Displays the 30-day history of the Anchor Yield Reserve.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file, by default False | False | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>