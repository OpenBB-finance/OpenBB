---
title: ln
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ln

<Tabs>
<TabItem value="model" label="Model" default>

## etf_financedatabase_model.get_etfs_by_name

```python title='openbb_terminal/etf/financedatabase_model.py'
def get_etfs_by_name(name: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/financedatabase_model.py#L15)

Description: Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | Search by name to find ETFs matching the criteria. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Dict[str, Any] | Dictionary with ETFs that match a certain name |

## Examples



</TabItem>
<TabItem value="view" label="View">

## etf_financedatabase_view.display_etf_by_name

```python title='openbb_terminal/etf/financedatabase_view.py'
def display_etf_by_name(name: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/financedatabase_view.py#L18)

Description: Display a selection of ETFs based on name filtered by total assets. [Source: Finance Database]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | Search by name to find ETFs matching the criteria. | None | False |
| limit | int | Limit of ETFs to display | None | False |
| export | str | Type of format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>