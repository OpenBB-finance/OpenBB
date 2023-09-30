---
title: getdd
description: OpenBB SDK Function
---

# getdd

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

