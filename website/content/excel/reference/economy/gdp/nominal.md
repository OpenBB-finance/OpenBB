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

```jsx<span style={color: 'red'}>=OBB.ECONOMY.GDP.NOMINAL([provider];[units];[start_date];[end_date];[country])</span>```

### Example

```excel wordwrap
=OBB.ECONOMY.GDP.NOMINAL()
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: oecd, defaults to oecd. | True |
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
