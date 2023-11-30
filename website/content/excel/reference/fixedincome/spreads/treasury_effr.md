<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Select Treasury Bill.

Get Selected Treasury Bill Minus Federal Funds Rate.
Constant maturity is the theoretical value of a U.S. Treasury that is based on recent values of
auctioned U.S. Treasuries.
The value is obtained by the U.S. Treasury on a daily basis through interpolation of the Treasury
yield curve which, in turn, is based on closing bid-yields of actively-traded Treasury securities.

```excel wordwrap
=OBB.FIXEDINCOME.SPREADS.TREASURY_EFFR(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| maturity | string | The maturity | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | SelectedTreasuryBill Rate.  |
