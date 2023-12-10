---
title: treasury_rates
description: Government Treasury Rates
keywords: 
- fixedincome
- government
- treasury_rates
---

<!-- markdownlint-disable MD041 -->

Government Treasury Rates.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.GOVERNMENT.TREASURY_RATES(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| month_1 | 1 month treasury rate.  |
| month_2 | 2 month treasury rate.  |
| month_3 | 3 month treasury rate.  |
| month_6 | 6 month treasury rate.  |
| year_1 | 1 year treasury rate.  |
| year_2 | 2 year treasury rate.  |
| year_3 | 3 year treasury rate.  |
| year_5 | 5 year treasury rate.  |
| year_7 | 7 year treasury rate.  |
| year_10 | 10 year treasury rate.  |
| year_20 | 20 year treasury rate.  |
| year_30 | 30 year treasury rate.  |
