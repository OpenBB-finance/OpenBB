<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

ETF Country weighting.

```excel wordwrap
=OBB.ETF.COUNTRIES(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. (ETF) | false |
| provider | string | Options: fmp | true |

## Data

| Name | Description |
| ---- | ----------- |
| country | The country of the exposure.  Corresponding values are normalized percentage points.  |
