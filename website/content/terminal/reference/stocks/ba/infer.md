---
title: infer
description: The documentation guide on 'infer', a tool used for quick sentiment inference
  from latest tweets that contain the ticker using vader sentiment analysis. It provides
  parameters to set the tweet limit and also includes examples of usage
keywords:
- infer
- vader sentiment analysis
- Twitter
- tweets
- sentiment inference
- stock
- limit
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ba/infer - Reference | OpenBB Terminal Docs" />

Print quick sentiment inference from last tweets that contain the ticker. This model splits the text into character-level tokens and uses vader sentiment analysis. [Source: Twitter]

### Usage

```python
infer [-l LIMIT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | limit of latest tweets to infer from. | 100 | True | None |


---

## Examples

```python
2022 Feb 19, 13:05 (🦋) /stocks/ba/ $ infer
From: 2022-02-19 17:08:20
To:   2022-02-19 18:04:18
100 tweets were analyzed.
Frequency of approx 1 tweet every 34 seconds.
The summed compound sentiment of AAPL is: 13.2
The average compound sentiment of AAPL is: 0.13
Of the last 100 tweets, 45.00 % had a higher positive sentiment
Of the last 100 tweets, 18.00 % had a higher negative sentiment
```
---
