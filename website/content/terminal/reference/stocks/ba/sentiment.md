---
title: sentiment
description: The page provides a sentiment analysis tool that predicts in-depth sentiment
  from recent tweets containing pre-specified stock tickers. It offers customizable
  parameters including the limit of tweets to extract per hour and the number of past
  days to extract tweets. Additionally, users can choose to show a corresponding change
  in the stock price, enhancing the analysis.
keywords:
- sentiment
- tweets analysis
- stock market sentiment
- Twitter data analysis
- predictive sentiment analysis
- stock market data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ba/sentiment - Reference | OpenBB Terminal Docs" />

Plot in-depth sentiment predicted from tweets from last days that contain pre-defined ticker. [Source: Twitter]

### Usage

```python
sentiment [-l LIMIT] [-d N_DAYS_PAST] [-c]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | limit of tweets to extract per hour. | 15 | True | None |
| n_days_past | number of days in the past to extract tweets. | 6 | True | None |
| compare | show corresponding change in stock price | False | True | None |


---

## Examples

```python
2022 Feb 19, 13:16 (🦋) /stocks/ba/ $ sentiment
From 2022-02-19 retrieving 360 tweets (15 tweets/hour)
From 2022-02-18 retrieving 360 tweets (15 tweets/hour)
From 2022-02-17 retrieving 360 tweets (15 tweets/hour)
From 2022-02-16 retrieving 360 tweets (15 tweets/hour)
From 2022-02-15 retrieving 360 tweets (15 tweets/hour)
From 2022-02-14 retrieving 360 tweets (15 tweets/hour)
From 2022-02-13 retrieving 360 tweets (15 tweets/hour)
```
---
