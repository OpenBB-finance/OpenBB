---
title: nominal
description: Nominal GDP Data
keywords: 
- economy
- gdp
- nominal
---

<!-- markdownlint-disable MD041 -->

Nominal GDP Data.

## Syntax

```excel wordwrap
=OBB.ECONOMY.GDP.NOMINAL(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: oecd | True |
| units | Text | The unit of measurement for the data. Units to get nominal GDP in. Either usd or usd_cap indicating per capita. | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| country | Text | Country to get GDP for. (provider: oecd) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Nominal GDP value on the date.  |
