---
title: fails_to_deliver
description: Learn how to retrieve reported Fail-to-deliver (FTD) data using the OBB.equity.shorts.fails_to_deliver
  function in Python. Explore the available parameters for symbol selection and provider
  options. Understand the data returned, including settlement date, symbol, quantity
  of fails, and more.
keywords: 
- Fail-to-deliver data
- Fail-to-deliver reporting
- Equity FTD
- Symbol data
- Provider selection
- Limiting number of reports
- Skipping reports
- Settlement date
- CUSIP
- Quantity of fails
- Previous closing price
---

<!-- markdownlint-disable MD041 -->

Get reported Fail-to-deliver (FTD) data.

## Syntax

```excel wordwrap
=OBB.EQUITY.SHORTS.FAILS_TO_DELIVER(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: sec | True |
| limit | Number | Limit the number of reports to parse, from most recent. Approximately 24 reports per year, going back to 2009. (provider: sec) | True |
| skip_reports | Number | Skip N number of reports from current. A value of 1 will skip the most recent report. (provider: sec) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| settlement_date | The settlement date of the fail.  |
| symbol | Symbol representing the entity requested in the data.  |
| cusip | CUSIP of the Security.  |
| quantity | The number of fails on that settlement date.  |
| price | The price at the previous closing price from the settlement date.  |
| description | The description of the Security.  |
