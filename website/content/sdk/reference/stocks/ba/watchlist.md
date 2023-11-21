---
title: watchlist
description: This page provides the syntax and details of the 'watchlist' function
  which fetches reddit users watchlists. It includes source code details, usage, parameters
  and return values.
keywords:
- Watchlist
- Reddit
- Python function
- Behavioral Analysis
- Source Code
- Returns
- Parameters
- Usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.watchlist - Reference | OpenBB SDK Docs" />

Get reddit users watchlists [Source: reddit].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L40)]

```python
openbb.stocks.ba.watchlist(limit: int = 5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of posts to look through | 5 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[List[praw.models.reddit.submission.Submission], dict, int] | List of reddit submissions,<br/>Dictionary of tickers and their count,<br/>Count of how many posts were analyzed. |
---
