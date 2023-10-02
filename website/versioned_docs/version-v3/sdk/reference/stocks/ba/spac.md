---
title: spac
description: OpenBB SDK Function
---

# spac

Get posts containing SPAC from top subreddits [Source: reddit].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L456)]

```python
openbb.stocks.ba.spac(limit: int = 5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of posts to get for each subreddit, by default 5 | 5 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, dict, int] | Dataframe of reddit submission,<br/>Dictionary of tickers and counts,<br/>Number of posts found. |
---

