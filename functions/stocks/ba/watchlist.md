---
title: watchlist
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# watchlist

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ba_reddit_model.get_watchlists

```python title='openbb_terminal/decorators.py'
def get_watchlists() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L40)

Description: Get reddit users watchlists [Source: reddit]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of posts to look through | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | List of reddit submissions |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ba_reddit_view.display_watchlist

```python title='openbb_terminal/decorators.py'
def display_watchlist() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L138)

Description: Print other users watchlist. [Source: Reddit]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Maximum number of submissions to look at | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>