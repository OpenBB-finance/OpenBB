---
title: getdd
description: OpenBB SDK Function
---

# getdd

## stocks_ba_reddit_model.get_due_dilligence

```python title='openbb_terminal/decorators.py'
def get_due_dilligence() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L716)

Description: Gets due diligence posts from list of subreddits [Source: reddit]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| limit | int | Number of posts to get | None | False |
| n_days | int | Number of days back to get posts | None | False |
| show_all_flairs | bool | Search through all flairs (apart from Yolo and Meme) | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of submissions |

## Examples

