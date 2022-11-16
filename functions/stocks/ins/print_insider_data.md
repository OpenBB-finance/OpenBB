---
title: print_insider_data
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# print_insider_data

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_insider_openinsider_model.get_print_insider_data

```python title='openbb_terminal/stocks/insider/openinsider_model.py'
def get_print_insider_data(type_insider: str, limit: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/openinsider_model.py#L1437)

Description: Print insider data

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| type_insider | str | Insider type of data. Available types can be accessed through get_insider_types(). | None | False |
| limit | int | Limit of data rows to display | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_insider_openinsider_view.print_insider_data

```python title='openbb_terminal/stocks/insider/openinsider_view.py'
def print_insider_data(type_insider: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/openinsider_view.py#L108)

Description: Print insider data

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| type_insider | str | Insider type of data. Available types can be accessed through get_insider_types(). | None | False |
| limit | int | Limit of data rows to display | None | False |
| export | str | Export data format | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>