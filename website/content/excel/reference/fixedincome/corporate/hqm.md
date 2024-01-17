---
title: HQM
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

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="FIXEDINCOME.CORPORATE.HQM | OpenBB Add-in for Excel Docs" />

High Quality Market Corporate Bond.  The HQM yield curve represents the high quality corporate bond market, i.e., corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms. These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve that is the market-weighted average (MWA) quality of high quality bonds.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.HQM([date];[yield_curve];[provider])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.HQM()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| date | Text | A specific date to get data for. | False |
| yield_curve | Text | The yield curve type. | False |
| provider | Text | Options: fred, defaults to fred. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | HighQualityMarketCorporateBond Rate.  |
| maturity | Maturity.  |
| yield_curve | The yield curve type.  |
| series_id | FRED series id. (provider: fred) |
