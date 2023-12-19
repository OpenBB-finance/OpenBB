---
title: getdd
description: This page explains the 'getdd' function. This function fetches due diligence
  posts from a list of subreddits. The source code link, parameters including the
  stock ticker, number of posts to fetch, and number of days back to fetch the posts,
  along with the return type are described.
keywords:
- getdd function
- stock ticker
- subreddits
- dataframe
- due diligence posts
- number of posts
- number of days
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.getdd - Reference | OpenBB SDK Docs" />

Gets due diligence posts from list of subreddits [Source: reddit].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L711)]

```python
openbb.stocks.ba.getdd(symbol: str, limit: int = 5, n_days: int = 3, show_all_flairs: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| limit | int | Number of posts to get | 5 | True |
| n_days | int | Number of days back to get posts | 3 | True |
| show_all_flairs | bool | Search through all flairs (apart from Yolo and Meme) | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of submissions |
---
