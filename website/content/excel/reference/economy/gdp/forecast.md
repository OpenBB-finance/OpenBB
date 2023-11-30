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

```excel wordwrap
=OBB.ECONOMY.GDP.FORECAST(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: oecd | true |
| period | string | Time period of the data to return. Units for nominal GDP period. Either quarter or annual. | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| type | string | Type of GDP to get forecast of. Either nominal or real. | true |
| country | string | Country to get GDP for. (provider: oecd) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Nominal GDP value on the date.  |
