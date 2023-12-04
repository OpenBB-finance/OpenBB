---
title: treasury_effr
description: This documentation page provides information about Treasury Bill data,
  including the selected Treasury Bill rate minus Federal Funds Rate. It explains
  the concept of constant maturity and the Treasury yield curve. The page also covers
  the parameters, returns, and data associated with the `obb.fixedincome.spreads.treasury_effr`
  function.
keywords: 
- Treasury Bill
- Selected Treasury Bill
- Federal Funds Rate
- Constant Maturity
- Treasury yield curve
- bid-yields
- US Treasuries
- obb.fixedincome.spreads.treasury_effr
- start_date
- end_date
- maturity
- provider
- results
- warnings
- chart
- metadata
- rate
- data
---

<!-- markdownlint-disable MD041 -->

Select Treasury Bill.  Get Selected Treasury Bill Minus Federal Funds Rate. Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of auctioned U.S. Treasuries. The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.SPREADS.TREASURY_EFFR(required;[optional])
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
| rate | SelectedTreasuryBill Rate.  |
