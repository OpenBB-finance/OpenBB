---
title: gacc
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# gacc

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_terramoney_fcd_model.get_account_growth

```python title='openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py'
def get_account_growth(cumulative: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py#L262)

Description: Get terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| cumulative | bool | distinguish between periodical and cumulative account growth data | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | historical data of accounts growth |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_terramoney_fcd_view.display_account_growth

```python title='openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py'
def display_account_growth(kind: str, cumulative: bool, limit: int, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py#L139)

Description: Display terra blockchain account growth history [Source: https://fcd.terra.dev/swagger]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | None | False |
| kind | str | display total account count or active account count. One from list [active, total] | None | False |
| cumulative | bool | Flag to show cumulative or discrete values. For active accounts only discrete value are available. | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>