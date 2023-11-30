<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Revenue Business Line. Business line revenue data.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.REVENUE_PER_SEGMENT(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |
| period | string | Time period of the data to return. | true |
| structure | string | Structure of the returned data. | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| business_line | Day level data containing the revenue of the business line.  |
