---
title: spacc
description: OpenBB SDK Function
---

# spacc

## stocks_ba_reddit_model.get_spac_community

```python title='openbb_terminal/decorators.py'
def get_spac_community() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L319)

Description: Get top tickers from r/SPACs [Source: reddit]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of posts to look at | None | False |
| popular | bool | Search by hot instead of new | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe of reddit submission |

## Examples

