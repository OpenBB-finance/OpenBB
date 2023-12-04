---
title: sofr
description: Learn about the Secured Overnight Financing Rate (SOFR), a measure of
  the cost of borrowing cash overnight collateralized by Treasury securities. Explore
  the SOFR Python function parameters, data returns, and more.
keywords: 
- Secured Overnight Financing Rate
- SOFR
- borrowing cash overnight
- collateralizing by Treasury securities
- SOFR python function
- SOFR parameters
- start_date
- end_date
- provider
- SOFR period
- returns
- results
- provider name
- warnings
- chart
- metadata
- data
- date
- rate
---

<!-- markdownlint-disable MD041 -->

Secured Overnight Financing Rate.  The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of borrowing cash overnight collateralizing by Treasury securities.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.SOFR(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| period | Text | Period of SOFR rate. (provider: fred) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | SOFR rate.  |
