<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Secured Overnight Financing Rate.

The Secured Overnight Financing Rate (SOFR) is a broad measure of the cost of
borrowing cash overnight collateralizing by Treasury securities.

```excel wordwrap
=OBB.FIXEDINCOME.SOFR(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| period | string | Period of SOFR rate. (provider: fred) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | SOFR rate.  |
