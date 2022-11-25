---
title: ueat
description: OpenBB Terminal Function
---

# ueat

Display number of unique ethereum addresses which made a transaction in given time interval, [Source: https://graphql.bitquery.io/]

### Usage

```python
ueat [-l LIMIT] [-s {date,uniqueSenders,transactions,averageGasPrice,mediumGasPrice,maximumGasPrice}] [-i {day,month,week}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number records. (Maximum available time period is 90 days.Depending on chosen time period, display N records will be recalculated. E.g.For interval: month, and number: 10, period of calculation equals to 300, but because of max days limit: 90, it will only return last 3 months (3 records). | 10 | True | range(1, 90) |
| sortby | Sort by given column. | date | True | date, uniqueSenders, transactions, averageGasPrice, mediumGasPrice, maximumGasPrice |
| interval | Time interval in which ethereum address made transaction. month, week or day. Maximum time period is 90 days (3 months, 14 weeks) | day | True | day, month, week |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
