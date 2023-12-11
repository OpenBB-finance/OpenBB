---
title: real
description: Learn about Real GDP Data and how to access it using the provided parameters.
  Find detailed descriptions of the available parameters and the data returned. Understand
  the structure of the returns and explore the data attributes.
keywords: 
- Real GDP Data
- parameters
- units
- start date
- end date
- provider
- country
- returns
- results
- GdpReal
- warnings
- chart
- metadata
- data
- date
- value
- documentation
---

<!-- markdownlint-disable MD041 -->

Real GDP Data.

## Syntax

```excel wordwrap
=OBB.ECONOMY.GDP.REAL(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: oecd | True |
| units | Text | The unit of measurement for the data. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).) | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| country | Text | Country to get GDP for. (provider: oecd) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Nominal GDP value on the date.  |
