---
title: sentiment
description: OpenBB Terminal Function
---

# sentiment

Plot in-depth sentiment predicted from tweets from last days that contain pre-defined ticker. [Source: Twitter]

### Usage

```python
usage: sentiment [-l LIMIT] [-d N_DAYS_PAST] [-c]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | limit of tweets to extract per hour. | 15 | True | None |
| n_days_past | number of days in the past to extract tweets. | 6 | True | None |
| compare | show corresponding change in stock price | False | True | None |
---

