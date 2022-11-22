---
title: spacc
description: OpenBB SDK Function
---

# spacc

Get top tickers from r/SPACs [Source: reddit].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L317)]

```python
openbb.stocks.ba.spacc(limit: int = 10, popular: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of posts to look at | 10 | True |
| popular | bool | Search by hot instead of new | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, dict] | Dataframe of reddit submission,<br/>Dictionary of tickers and number of mentions. |
---

