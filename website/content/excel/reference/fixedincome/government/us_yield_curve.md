<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

US Yield Curve. Get United States yield curve.

```excel wordwrap
=OBB.FIXEDINCOME.GOVERNMENT.US_YIELD_CURVE(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| date | string | A specific date to get data for. Defaults to the most recent FRED entry. | true |
| inflation_adjusted | boolean | Get inflation adjusted rates. | true |

## Data

| Name | Description |
| ---- | ----------- |
| maturity | Maturity of the treasury rate in years.  |
| rate | Associated rate given in decimal form (0.05 is 5%)  |
