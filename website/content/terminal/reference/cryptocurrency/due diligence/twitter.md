---
title: twitter
description: OpenBB Terminal Function
---

# twitter

Show last 10 tweets for given coin. You can display only N number of tweets with --limit parameter. You can sort data by date, user_name, status, retweet_count, like_count --sort parameter and also with --reverse flag to sort ascending. Displays: date, user_name, status, retweet_count, like_count

### Usage

```python
usage: twitter [-l LIMIT] [-s {date,user_name,status,retweet_count,like_count}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of records | 10 | True | None |
| sortby | Sort by given column. Default: date | date | True | date, user_name, status, retweet_count, like_count |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

