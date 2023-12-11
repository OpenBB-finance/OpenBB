---
title: historical_eps
description: Historical earnings-per-share for a given company
keywords: 
- equity
- fundamental
- historical_eps
---

<!-- markdownlint-disable MD041 -->

Historical earnings-per-share for a given company.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_EPS(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |
| limit | Number | The number of data entries to return. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| symbol | Symbol representing the entity requested in the data.  |
| announce_time | Timing of the earnings announcement.  |
| eps_actual | Actual EPS from the earnings date.  |
| eps_estimated | Estimated EPS for the earnings date.  |
| actual_eps | The actual earnings per share announced. (provider: fmp) |
| revenue_estimated | Estimated consensus revenue for the reporting period. (provider: fmp) |
| actual_revenue | The actual reported revenue. (provider: fmp) |
| reporting_time | The reporting time - e.g. after market close. (provider: fmp) |
| updated_at | The date when the data was last updated. (provider: fmp) |
| period_ending | The fiscal period end date. (provider: fmp) |
