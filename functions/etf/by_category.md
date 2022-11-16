---
title: by_category
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# by_category

<Tabs>
<TabItem value="model" label="Model" default>

## etf_financedatabase_model.get_etfs_by_category

```python title='openbb_terminal/etf/financedatabase_model.py'
def get_etfs_by_category(category: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/financedatabase_model.py#L56)

Description: Return a selection of ETFs based on category filtered by total assets.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| category | str | Search by category to find ETFs matching the criteria. | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| data | Dict | Dictionary with ETFs that match a certain description | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## etf_financedatabase_view.display_etf_by_category

```python title='openbb_terminal/etf/financedatabase_view.py'
def display_etf_by_category(category: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/financedatabase_view.py#L95)

Description: Display a selection of ETFs based on a category filtered by total assets.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| description | str | Search by description to find ETFs matching the criteria. | None | False |
| limit | int | Limit of ETFs to display | None | False |
| export | str | Type of format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>