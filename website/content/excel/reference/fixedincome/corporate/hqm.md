<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

High Quality Market Corporate Bond.

The HQM yield curve represents the high quality corporate bond market, i.e.,
corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms.
These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve
that is the market-weighted average (MWA) quality of high quality bonds.

```excel wordwrap
=OBB.FIXEDINCOME.CORPORATE.HQM(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| date | string | A specific date to get data for. | true |
| yield_curve | string | The yield curve type. | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | HighQualityMarketCorporateBond Rate.  |
| maturity | Maturity.  |
| yield_curve | The yield curve type.  |
