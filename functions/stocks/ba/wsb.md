---
title: wsb
description: OpenBB SDK Function
---

# wsb

## stocks_ba_reddit_model.get_wsb_community

```python title='openbb_terminal/decorators.py'
def get_wsb_community() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L607)

Description: Get wsb posts [Source: reddit]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of posts to get, by default 10 | 10 | True |
| new | bool | Flag to sort by new instead of hot, by default False | False | True |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of reddit submissions |

## Examples

