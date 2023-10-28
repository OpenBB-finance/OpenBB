---
title: popular
description: This page contains a python function to get popular tickers from a list
  of subreddits. The function leverages the OpenBB.Finance Terminal to analyze the
  behavioral analysis of posts from Reddit.
keywords:
- OpenBB.Finance Terminal
- Reddit ticker analysis
- Python function
- Behavioral analysis
- Popular tickers
- Subreddits
- Post analysis
- DataFrames
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.popular - Reference | OpenBB SDK Docs" />

Get popular tickers from list of subreddits [Source: reddit].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L145)]

```python
openbb.stocks.ba.popular(limit: int = 10, post_limit: int = 50, subreddits: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of top tickers to get | 10 | True |
| post_limit | int | How many posts to analyze in each subreddit | 50 | True |
| subreddits | str | String of comma separated subreddits. |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of top tickers from supplied subreddits |
---
