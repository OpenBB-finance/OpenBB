<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the holdings filing date for an individual ETF.

```excel wordwrap
=OBB.ETF.HOLDINGS_DATE(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. (ETF) | false |
| provider | string | Options: fmp | true |
| cik | string | The CIK of the filing entity. Overrides symbol. (provider: fmp) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
