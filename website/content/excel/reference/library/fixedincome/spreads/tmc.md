---
title: tmc
description: Learn about Treasury Constant Maturity and how to get data for it. Understand
  constant maturity calculation and the use of Treasury yield curve and Treasury securities.
  Explore parameters like start date, end date, maturity, and provider. Get a list
  of results, warnings, and metadata along with a chart depicting the Treasury Constant
  Maturity rate.
keywords: 
- Treasury Constant Maturity
- data
- U.S. Treasury
- yield curve
- Treasury securities
- start date
- end date
- maturity
- provider
- results
- warnings
- chart
- metadata
- rate
---

<!-- markdownlint-disable MD041 -->

Treasury Constant Maturity.  Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity. Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.SPREADS.TMC(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| maturity | Text | The maturity | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | TreasuryConstantMaturity Rate.  |
