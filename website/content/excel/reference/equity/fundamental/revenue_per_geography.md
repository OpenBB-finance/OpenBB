<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Revenue Geographic. Geographic revenue data.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.REVENUE_PER_GEOGRAPHY(required, [optional])
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
| geographic_segment | Day level data containing the revenue of the geographic segment.  |
| americas | Revenue from the the American segment.  |
| europe | Revenue from the the European segment.  |
| greater_china | Revenue from the the Greater China segment.  |
| japan | Revenue from the the Japan segment.  |
| rest_of_asia_pacific | Revenue from the the Rest of Asia Pacific segment.  |
