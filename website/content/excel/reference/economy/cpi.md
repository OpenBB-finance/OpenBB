---
title: cpi
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

<!-- markdownlint-disable MD041 -->

Consumer Price Index (CPI) Data.

```excel wordwrap
=OBB.ECONOMY.CPI(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| countries | any | The country or countries to get data. | false |
| provider | string | Options: fred | true |
| units | string | The unit of measurement for the data. Options: - `growth_previous`: growth from the previous period - `growth_same`: growth from the same period in the previous year - `index_2015`: index with base year 2015. | true |
| frequency | string | The frequency of the data. Options: `monthly`, `quarter`, and `annual`. | true |
| harmonized | boolean | Whether you wish to obtain harmonized data. | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
