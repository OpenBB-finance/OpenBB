---
title: search
description: Discover OpenBB's robust functionality to sort repos by stars or forks,
  with an additional category filter feature. The result is straightforwardly produced
  as a DataFrame. Source code available.
keywords:
- OpenBB finance
- Repo sorter
- Star ranking
- Fork ranking
- Category filter
- Python API
- Financial data extraction
- Dataframe results
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.oss.search - Reference | OpenBB SDK Docs" />

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
