---
title: overview
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# overview

<Tabs>
<TabItem value="model" label="Model" default>

## mutual_funds_investpy_model.get_overview

```python title='openbb_terminal/mutual_funds/investpy_model.py'
def get_overview(country: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/investpy_model.py#L49)

Description: None

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to get overview for | None | False |
| limit | int | Number of results to get | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing overview |

## Examples



</TabItem>
<TabItem value="view" label="View">

## mutual_funds_investpy_view.display_overview

```python title='openbb_terminal/mutual_funds/investpy_view.py'
def display_overview(country: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/investpy_view.py#L74)

Description: Displays an overview of the main funds from a country.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to get overview for | None | False |
| limit | int | Number to show | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>