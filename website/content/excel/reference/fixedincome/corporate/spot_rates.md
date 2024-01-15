---
title: spot_rates
description: Learn about spot rates and how they are used to calculate the yield on
  a bond. Understand the concept of discounting and its application in evaluating
  pension liabilities. Explore the parameters needed to query and retrieve spot rate
  data. Get the serializable results, provider information, warnings, chart, and metadata
  associated with the query. Access the spot rate data including the date and rate.
keywords: 
- spot rates
- yield
- bond
- zero coupon bond
- interest rate
- discounting
- pension liability
- maturities
- query
- results
- provider
- warnings
- chart
- metadata
- data
- date
- rate
---

<!-- markdownlint-disable MD041 -->

Spot Rates.  The spot rates for any maturity is the yield on a bond that provides a single payment at that maturity. This is a zero coupon bond. Because each spot rate pertains to a single cashflow, it is the relevant interest rate concept for discounting a pension liability at the same maturity.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.SPOT_RATES([start_date];[end_date];[maturity];[category];[provider])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.SPOT_RATES()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| maturity | Any | The maturities in years. | False |
| category | Any | The category. | False |
| provider | Text | Options: fred, defaults to fred. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | Spot Rate.  |
