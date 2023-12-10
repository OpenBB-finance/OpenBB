---
title: forecast
description: Forecasted GDP Data
keywords: 
- economy
- gdp
- forecast
---

<!-- markdownlint-disable MD041 -->

Forecasted GDP Data.

## Syntax

```excel wordwrap
=OBB.ECONOMY.GDP.FORECAST(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: oecd | True |
| period | Text | Time period of the data to return. Units for nominal GDP period. Either quarter or annual. | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| type | Text | Type of GDP to get forecast of. Either nominal or real. | True |
| country | Text | Country to get GDP for. (provider: oecd) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Nominal GDP value on the date.  |
