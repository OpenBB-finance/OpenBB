---
title: wsb
description: OpenBB SDK Function
---

# wsb

Get wsb posts [Source: reddit].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L602)]

```python
openbb.stocks.ba.wsb(limit: int = 10, new: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of posts to get, by default 10 | 10 | True |
| new | bool | Flag to sort by new instead of hot, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of reddit submissions |
---

