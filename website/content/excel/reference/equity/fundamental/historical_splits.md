<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Splits. Historical splits data.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_SPLITS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| label | Label of the historical stock splits.  |
| numerator | Numerator of the historical stock splits.  |
| denominator | Denominator of the historical stock splits.  |
