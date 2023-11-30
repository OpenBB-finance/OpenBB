<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fuzzy search for Industry Titles, Reporting Office, and SIC Codes.

```excel wordwrap
=OBB.REGULATORS.SEC.SIC_SEARCH(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: sec | true |
| query | string | Search query. | true |
| use_cache | boolean | Whether to use the cache or not. The full list will be cached for seven days if True. (provider: sec) | true |

## Data

| Name | Description |
| ---- | ----------- |
| sic | Sector Industrial Code (SIC) (provider: sec) |
| industry | Industry title. (provider: sec) |
| office | Reporting office within the Corporate Finance Office (provider: sec) |
