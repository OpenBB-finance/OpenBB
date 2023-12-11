---
title: calendar
description: The Economic Calendar provides information on economic events and data.
  Use the OBB Python function `obb.economy.calendar()` to retrieve economic calendar
  data. The function accepts parameters such as start date, end date, provider, country,
  importance, and group. It returns a list of economic calendar data, including the
  date, event, reference, source, actual value, previous value, consensus value, and
  forecast value. The data can be filtered by provider such as FMP, Nasdaq, or Trading
  Economics.
keywords: 
- economic calendar
- python obb.economy.calendar
- parameters
- start date
- end date
- provider
- country
- importance
- group
- returns
- data
- date
- event
- reference
- source
- source url
- actual
- previous
- consensus
- forecast
- url
- currency
- unit
- change
- change percent
- updated at
- created at
- description
---

<!-- markdownlint-disable MD041 -->

Economic Calendar.

## Syntax

```excel wordwrap
=OBB.ECONOMY.CALENDAR(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp, tradingeconomics | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| country | Any | Country of the event (provider: tradingeconomics) | True |
| importance | Text | Importance of the event. (provider: tradingeconomics) | True |
| group | Text | Grouping of events (provider: tradingeconomics) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| country | Country of event.  |
| event | Event name.  |
| reference | Abbreviated period for which released data refers to.  |
| source | Source of the data.  |
| sourceurl | Source URL.  |
| actual | Latest released value.  |
| previous | Value for the previous period after the revision (if revision is applicable).  |
| consensus | Average forecast among a representative group of economists.  |
| forecast | Trading Economics projections  |
| url | Trading Economics URL  |
| importance | Importance of the event. 1-Low, 2-Medium, 3-High  |
| currency | Currency of the data.  |
| unit | Unit of the data.  |
| change | Value change since previous. (provider: fmp) |
| change_percent | Percentage change since previous. (provider: fmp) |
| updated_at | Last updated timestamp. (provider: fmp) |
| created_at | Created at timestamp. (provider: fmp) |
