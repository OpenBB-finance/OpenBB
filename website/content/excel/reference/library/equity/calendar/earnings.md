---
title: earnings
description: Learn how to retrieve upcoming and historical earnings calendar data
  using the OBB.equity.calendar.earnings Python function. The function allows you
  to specify symbols, limit the number of data entries, and choose a data provider.
  The returned data includes EPS, revenue, and other important details for the specified
  symbols and dates.
keywords: 
- earnings calendar
- upcoming earnings
- historical earnings
- Python function
- earnings data retrieval
- symbol
- limit
- provider
- data entries
- chart
- metadata
- data
- EPS
- revenue
- estimated EPS
- estimated revenue
- date
- time
- updated from date
- fiscal date ending
---

<!-- markdownlint-disable MD041 -->

Upcoming and Historical earnings calendar.

## Syntax

```excel wordwrap
=OBB.EQUITY.CALENDAR.EARNINGS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| report_date | The date of the earnings report.  |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the entity.  |
| eps_previous | The earnings-per-share from the same previously reported period.  |
| eps_consensus | The analyst conesus earnings-per-share estimate.  |
| actual_eps | The actual earnings per share announced. (provider: fmp) |
| actual_revenue | The actual reported revenue. (provider: fmp) |
| revenue_consensus | The revenue forecast consensus. (provider: fmp) |
| period_ending | The fiscal period end date. (provider: fmp) |
| reporting_time | The reporting time - e.g. after market close. (provider: fmp) |
| updated_date | The date the data was updated last. (provider: fmp) |
