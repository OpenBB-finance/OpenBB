<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Upcoming and Historical earnings calendar.

```excel wordwrap
=OBB.EQUITY.CALENDAR.EARNINGS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |

## Data

| Name | Description |
| ---- | ----------- |
| report_date | The date of the earnings report.  |
| symbol | Symbol representing the entity requested in the data.  |
| name | Name of the entity.  |
| eps_previous | The earnings-per-share from the same previously reported period.  |
| eps_consensus | The analyst conesus earnings-per-share estimate.  |
| actual_eps | The actual earnings per share announced. (provider: fmp) |
| actual_revenue | The actual reported revenue. (provider: fmp) |
| revenue_consensus | The revenue forecast consensus. (provider: fmp) |
| period_ending | The fiscal period end date. (provider: fmp) |
| reporting_time | The reporting time - e.g. after market close. (provider: fmp) |
| updated_date | The date the data was updated last. (provider: fmp) |
