---
title: search
description: OpenBB SDK Function
---

# search

Get repos sorted by stars or forks. Can be filtered by categories.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/github_model.py#L56)]

```python
openbb.alt.oss.search(sortby: str = "stars", page: int = 1, categories: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Sort repos by {stars, forks} | stars | True |
| categories | str | Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None |  | True |
| page | int | Page number to get repos | 1 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with repos |
---

