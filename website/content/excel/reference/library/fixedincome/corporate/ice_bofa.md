---
title: ice_bofa
description: Learn about ICE BofA US Corporate Bond Indices, including the ICE BofA
  US Corporate Index and parameters for the `obb.fixedincome.corporate.ice_bofa` function.
  Find out how to retrieve historical data and explore the available categories and
  areas.
keywords: 
- ICE BofA US Corporate Bond Indices
- ICE BofA US Corporate Index
- US dollar denominated investment grade corporate debt
- Moody's
- S&P
- Fitch
- investment grade rating
- final maturity
- rebalance date
- fixed coupon schedule
- minimum amount outstanding
- US Corporate Master Index
- start date
- end date
- index type
- provider
- fred
- category
- area
- grade
- options
- returns
- results
- warnings
- chart
- metadata
- data
- rate
---

<!-- markdownlint-disable MD041 -->

ICE BofA US Corporate Bond Indices.  The ICE BofA US Corporate Index tracks the performance of US dollar denominated investment grade corporate debt publicly issued in the US domestic market. Qualifying securities must have an investment grade rating (based on an average of Moody’s, S&P and Fitch), at least 18 months to final maturity at the time of issuance, at least one year remaining term to final maturity as of the rebalance date, a fixed coupon schedule and a minimum amount outstanding of $250 million. The ICE BofA US Corporate Index is a component of the US Corporate Master Index.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.ICE_BOFA(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| index_type | Text | The type of series. | True |
| category | Text | The type of category. (provider: fred) | True |
| area | Text | The type of area. (provider: fred) | True |
| grade | Text | The type of grade. (provider: fred) | True |
| options | Boolean | Whether to include options in the results. (provider: fred) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | ICE BofA US Corporate Bond Indices Rate.  |
