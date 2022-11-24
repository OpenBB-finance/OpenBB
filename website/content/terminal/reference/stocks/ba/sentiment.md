---
title: sentiment
description: OpenBB Terminal Function
---

# sentiment

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
