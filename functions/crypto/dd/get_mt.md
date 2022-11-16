---
title: get_mt
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# get_mt

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_messari_model.get_available_timeseries

```python title='openbb_terminal/cryptocurrency/due_diligence/messari_model.py'
def get_available_timeseries(only_free: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L34)

Description: Returns available messari timeseries

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| only_free | bool | Display only timeseries available for free | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | available timeseries |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_messari_view.display_messari_timeseries_list

```python title='openbb_terminal/decorators.py'
def display_messari_timeseries_list() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L49)

Description: Display messari timeseries list

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | number to show | None | False |
| query | str | Query to search across all messari timeseries | None | False |
| only_free | bool | Display only timeseries available for free | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>