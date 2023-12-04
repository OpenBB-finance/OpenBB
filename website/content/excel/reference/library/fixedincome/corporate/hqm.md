---
title: hqm
description: Learn about the HQM yield curve and the high quality corporate bond market.
  Get information on AAA, AA, and A bonds, market-weighted average quality, corporate
  bond rates, maturity, yield curve type, provider, and data.
keywords: 
- HQM yield curve
- high quality corporate bond market
- AAA bonds
- AA bonds
- A bonds
- market-weighted average quality
- corporate bond rates
- maturity
- yield curve type
- provider
- fred
- data
---

<!-- markdownlint-disable MD041 -->

High Quality Market Corporate Bond.  The HQM yield curve represents the high quality corporate bond market, i.e., corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms. These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve that is the market-weighted average (MWA) quality of high quality bonds.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.HQM(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| date | Text | A specific date to get data for. | True |
| yield_curve | Text | The yield curve type. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | HighQualityMarketCorporateBond Rate.  |
| maturity | Maturity.  |
| yield_curve | The yield curve type.  |
