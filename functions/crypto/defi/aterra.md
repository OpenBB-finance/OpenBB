---
title: aterra
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# aterra

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_terraengineer_model.get_history_asset_from_terra_address

```python title='openbb_terminal/cryptocurrency/defi/terraengineer_model.py'
def get_history_asset_from_terra_address(asset: str, address: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terraengineer_model.py#L19)

Description: Returns historical data of an asset in a certain terra address

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | str | Terra asset {ust,luna,sdt} | None | False |
| address | str | Terra address. Valid terra addresses start with 'terra' | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | historical data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_terraengineer_view.display_terra_asset_history

```python title='openbb_terminal/cryptocurrency/defi/terraengineer_view.py'
def display_terra_asset_history(asset: str, address: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terraengineer_view.py#L29)

Description: Displays the 30-day history of specified asset in terra address

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | str | Terra asset {ust,luna,sdt} | None | False |
| address | str | Terra address. Valid terra addresses start with 'terra' | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>