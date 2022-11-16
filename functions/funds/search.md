---
title: search
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# search

<Tabs>
<TabItem value="model" label="Model" default>

## mutual_funds_investpy_model.search_funds

```python title='openbb_terminal/mutual_funds/investpy_model.py'
def search_funds(by: str, value: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/investpy_model.py#L20)

Description: Search investpy for matching funds

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| by | str | Field to match on.  Can be name, issuer, isin or symbol | None | False |
| value | str | String that will be searched for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing matches |

## Examples



</TabItem>
<TabItem value="view" label="View">

## mutual_funds_investpy_view.display_search

```python title='openbb_terminal/mutual_funds/investpy_view.py'
def display_search(by: str, value: str, country: str, limit: int, sortby: str, ascend: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/mutual_funds/investpy_view.py#L27)

Description: Display results of searching for Mutual Funds

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| by | str | Field to match on.  Can be name, issuer, isin or symbol | None | False |
| value | str | String that will be searched for | None | False |
| country | str | Country to filter on | None | False |
| limit | int | Number to show | None | False |
| sortby | str | Column to sort by | None | False |
| ascend | bool | Flag to sort in ascending order | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>