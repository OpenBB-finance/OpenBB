---
title: info
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# info

<Tabs>
<TabItem value="model" label="Model" default>

## mutual_funds_investpy_model.get_fund_info

```python title='openbb_terminal/mutual_funds/investpy_model.py'
def get_fund_info(name: str, country: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/investpy_model.py#L145)

Description: None

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | Name of fund (not symbol) to get information | None | False |
| country | str | Country of fund | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of fund information |

## Examples



</TabItem>
<TabItem value="view" label="View">

## mutual_funds_investpy_view.display_fund_info

```python title='openbb_terminal/mutual_funds/investpy_view.py'
def display_fund_info(name: str, country: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/investpy_view.py#L104)

Description: Display fund information.  Finds name from symbol first if name is false

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| name | str | Fund name to get info for | None | False |
| country | str | Country of fund | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>