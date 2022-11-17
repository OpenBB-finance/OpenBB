---
title: search
description: OpenBB SDK Function
---

# search

## alt_oss_github_model.search_repos

```python title='openbb_terminal/alternative/oss/github_model.py'
def search_repos(sortby: str, page: int, categories: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_model.py#L54)

Description: Get repos sorted by stars or forks. Can be filtered by categories

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Sort repos by {stars, forks} | None | False |
| categories | str | Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None | None | False |
| page | int | Page number to get repos | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame with list of repos | None |

## Examples

