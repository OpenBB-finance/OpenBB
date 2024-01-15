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
=OBB.ECONOMY.GDP.FORECAST([period];[start_date];[end_date];[type];[provider];[country])
```

### Example

```excel wordwrap
=OBB.ECONOMY.GDP.FORECAST()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| period | Text | Time period of the data to return. Units for nominal GDP period. Either quarter or annual. | False |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| type | Text | Type of GDP to get forecast of. Either nominal or real. | False |
| provider | Text | Options: oecd, defaults to oecd. | False |
| country | Text | Country to get GDP for. (provider: oecd) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Nominal GDP value on the date.  |
