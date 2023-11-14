---
title: text_sent
description: Learn how to use the Text Sentiment Analysis function of OpenBB's Reddit
  Model. Understand the sentiment of a post and related comments, providing valuable
  insights into stock market trends.
keywords:
- Text sentiment analysis
- Stock market sentiment
- Behavioural analysis
- Comment analysis
- Post analysis
- Reddit model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.text_sent - Reference | OpenBB SDK Docs" />

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
