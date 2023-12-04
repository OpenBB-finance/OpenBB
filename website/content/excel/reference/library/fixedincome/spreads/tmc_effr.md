---
title: tmc_effr
description: Learn how to select Treasury Constant Maturity and access data for it
  using the obb.fixedincome.spreads.tmc_effr function. Understand constant maturity,
  Treasury yield curve, bid-yields, and Treasury securities. Explore the parameters
  and data returned by the function.
keywords: 
- Treasury Constant Maturity
- data for Treasury Constant Maturity
- constant maturity
- U.S. Treasury
- Treasury yield curve
- yield curve interpolation
- bid-yields
- Treasury securities
- obb.fixedincome.spreads.tmc_effr
- start_date
- end_date
- maturity
- provider
- results
- warnings
- chart
- metadata
- date
- rate
---

<!-- markdownlint-disable MD041 -->

Select Treasury Constant Maturity.  Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.SPREADS.TMC_EFFR(required;[optional])
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
| rate | Selected Treasury Constant Maturity Rate.  |
