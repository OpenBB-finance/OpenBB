---
title: us_yield_curve
description: Learn about the US Yield Curve and how to retrieve United States yield
  curve data using the OBB.fixedincome.government.us_yield_curve function. Explore
  parameters like date, inflation adjustment, and provider. Understand the returned
  results, including the chart, metadata, and warnings. Discover the data structure,
  including maturity and rate.
keywords: 
- US Yield Curve
- United States yield curve
- yield curve
- government bonds
- fixed income
- rates
- inflation adjusted
- FRED provider
- data
- maturity
- treasury rate
- rate
---

<!-- markdownlint-disable MD041 -->

US Yield Curve. Get United States yield curve.

```excel wordwrap
=OBB.FIXEDINCOME.GOVERNMENT.US_YIELD_CURVE(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| date | string | A specific date to get data for. Defaults to the most recent FRED entry. | true |
| inflation_adjusted | boolean | Get inflation adjusted rates. | true |

## Data

| Name | Description |
| ---- | ----------- |
| maturity | Maturity of the treasury rate in years.  |
| rate | Associated rate given in decimal form (0.05 is 5%)  |
