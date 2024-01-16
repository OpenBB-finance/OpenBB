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
=OBB.ECONOMY.GDP.REAL([units];[start_date];[end_date];[provider];[country])
```

### Example

```excel wordwrap
=OBB.ECONOMY.GDP.REAL()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| units | Text | The unit of measurement for the data. Either idx (indicating 2015=100), qoq (previous period) or yoy (same period, previous year).) | False |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: oecd, defaults to oecd. | False |
| country | Text | Country to get GDP for. (provider: oecd) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Nominal GDP value on the date.  |
