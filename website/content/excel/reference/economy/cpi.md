---
title: CPI
description: Get Consumer Price Index (CPI) data for various countries and calculate
  inflation measurements. This economic indicator provides insights into the growth
  rate of prices on a monthly, quarterly, and annual basis. Harmonized CPI data is
  also available. Specify the start and end dates for the desired data range. The
  data provider and metadata information are included in the results.
keywords: 
- Consumer Price Index (CPI) Data
- CPI data
- CPI calculation
- inflation measurement
- economic indicator
- country-wise CPI data
- growth rate
- monthly CPI
- quarterly CPI
- annual CPI
- harmonized CPI
- start date
- end date
- data provider
- metadata info
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ECONOMY.CPI | OpenBB Add-in for Excel Docs" />

Consumer Price Index (CPI).  Returns either the rescaled index value, or a rate of change (inflation).

## Syntax

```excel wordwrap
=OBB.ECONOMY.CPI(countries;[units];[frequency];[harmonized];[start_date];[end_date];[provider])
```

### Example

```excel wordwrap
=OBB.ECONOMY.CPI("united_states")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **countries** | **Any** | **The country or countries to get data.** | **True** |
| units | Text | The unit of measurement for the data. Options: - `growth_previous`: Percent growth from the previous period. If monthly data, this is month-over-month, etc - `growth_same`: Percent growth from the same period in the previous year. If looking at monthly data, this would be year-over-year, etc. - `index_2015`: Rescaled index value, such that the value in 2015 is 100. | False |
| frequency | Text | The frequency of the data. Options: `monthly`, `quarter`, and `annual`. | False |
| harmonized | Boolean | Whether you wish to obtain harmonized data. | False |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: fred, defaults to fred. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
