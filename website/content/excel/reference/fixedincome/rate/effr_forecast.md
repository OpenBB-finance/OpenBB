<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fed Funds Rate Projections.

The projections for the federal funds rate are the value of the midpoint of the
projected appropriate target range for the federal funds rate or the projected
appropriate target level for the federal funds rate at the end of the specified
calendar year or over the longer run.

```excel wordwrap
=OBB.FIXEDINCOME.RATE.EFFR_FORECAST(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| long_run | boolean | Flag to show long run projections (provider: fred) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| range_high | High projection of rates.  |
| central_tendency_high | Central tendency of high projection of rates.  |
| median | Median projection of rates.  |
| range_midpoint | Midpoint projection of rates.  |
| central_tendency_midpoint | Central tendency of midpoint projection of rates.  |
| range_low | Low projection of rates.  |
| central_tendency_low | Central tendency of low projection of rates.  |
