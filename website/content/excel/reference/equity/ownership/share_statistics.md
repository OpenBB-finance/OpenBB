<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Share Statistics. Share statistics for a given company.

```excel wordwrap
=OBB.EQUITY.OWNERSHIP.SHARE_STATISTICS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp, intrinio | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| free_float | Percentage of unrestricted shares of a publicly-traded company.  |
| float_shares | Number of shares available for trading by the general public.  |
| outstanding_shares | Total number of shares of a publicly-traded company.  |
| source | Source of the received data.  |
| adjusted_outstanding_shares | Total number of shares of a publicly-traded company, adjusted for splits. (provider: intrinio) |
| public_float | Aggregate market value of the shares of a publicly-traded company. (provider: intrinio) |
