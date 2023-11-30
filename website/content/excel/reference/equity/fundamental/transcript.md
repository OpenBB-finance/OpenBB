<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Earnings Call Transcript. Earnings call transcript for a given company.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.TRANSCRIPT(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| year | number | Year of the earnings call transcript. | false |
| provider | string | Options: fmp | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| quarter | Quarter of the earnings call transcript.  |
| year | Year of the earnings call transcript.  |
| date | The date of the data.  |
| content | Content of the earnings call transcript.  |
