---
title: redditsent
description: A documentation on redditsent function. It is used to find posts related
  to a specific search term from Reddit. The function provides comprehensive search
  and categorization of results based on user-preferences.
keywords:
- redditsent
- Search function
- Reddit posts
- Behavioral analysis
- Python function
- Ticker symbol
- post categorization
- Comprehensive search
- subreddits
- dataframe
- polarity scores
- average polarity score
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.redditsent - Reference | OpenBB SDK Docs" />

Finds posts related to a specific search term in Reddit.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L864)]

```python
openbb.stocks.ba.redditsent(symbol: str, limit: int = 100, sortby: str = "relevance", time_frame: str = "week", full_search: bool = True, subreddits: str = "all")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to search for | None | False |
| limit | int | Number of posts to get per subreddit | 100 | True |
| sortby | str | Search type (Possibilities: "relevance", "hot", "top", "new", or "comments") | relevance | True |
| time_frame | str | Relative time of post (Possibilities: "hour", "day", "week", "month", "year", "all") | week | True |
| full_search | bool | Enable comprehensive search for ticker | True | True |
| subreddits | str | Comma-separated list of subreddits | all | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe of submissions related to the search term,<br/>List of polarity scores,<br/>Average polarity score. |
---
