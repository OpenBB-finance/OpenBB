---
title: apy
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# apy

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_tools_model.calculate_apy

```python title='openbb_terminal/cryptocurrency/tools/tools_model.py'
def calculate_apy(apr: float, compounding_times: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/tools/tools_model.py#L19)

Description: Converts apr into apy

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| apr | float | value in percentage | None | False |
| compounding_times | int | number of compounded periods in a year | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | - pd.DataFrame: dataframe with results
- str: narrative version of results |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_tools_view.display_apy

```python title='openbb_terminal/cryptocurrency/tools/tools_view.py'
def display_apy(apr: float, compounding_times: int, narrative: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/tools/tools_view.py#L16)

Description: Displays APY value converted from APR

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| apr | float | value in percentage | None | False |
| compounding_times | int | number of compounded periods in a year | None | False |
| narrative | str | display narrative version instead of dataframe | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>