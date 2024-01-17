---
title: US_YIELD_CURVE
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

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="FIXEDINCOME.GOVERNMENT.US_YIELD_CURVE | OpenBB Add-in for Excel Docs" />

US Yield Curve. Get United States yield curve.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.GOVERNMENT.US_YIELD_CURVE([date];[inflation_adjusted];[provider])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.GOVERNMENT.US_YIELD_CURVE()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| date | Text | A specific date to get data for. Defaults to the most recent FRED entry. | False |
| inflation_adjusted | Boolean | Get inflation adjusted rates. | False |
| provider | Text | Options: fred, defaults to fred. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| maturity | Maturity of the treasury rate in years.  |
| rate | Associated rate given in decimal form (0.05 is 5%)  |
