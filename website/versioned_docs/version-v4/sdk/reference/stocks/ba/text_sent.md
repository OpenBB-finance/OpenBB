---
title: text_sent
description: OpenBB SDK Function
---

# text_sent

Find the sentiment of a post and related comments.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/reddit_model.py#L1049)]

```python
openbb.stocks.ba.text_sent(post_data: List[str])
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| post_data | list[str] | A post and its comments in string form | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| float | A number in the range [-1, 1] representing sentiment |
---

