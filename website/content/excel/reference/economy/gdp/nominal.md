---
title: NOMINAL
description: Nominal GDP Data
keywords: 
- economy
- gdp
- nominal
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ECONOMY.GDP.NOMINAL | OpenBB Add-in for Excel Docs" />

Nominal GDP Data.

## Syntax

```excel wordwrap
=OBB.ECONOMY.GDP.NOMINAL([units];[start_date];[end_date];[provider];[country])
```

### Example

```excel wordwrap
=OBB.ECONOMY.GDP.NOMINAL()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| units | Text | The unit of measurement for the data. Units to get nominal GDP in. Either usd or usd_cap indicating per capita. | False |
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
