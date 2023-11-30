<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get lists of SEC XML schema files by year.

```excel wordwrap
=OBB.REGULATORS.SEC.SCHEMA_FILES(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: sec | true |
| query | string | Search query. | true |
| url | string | Enter an optional URL path to fetch the next level. (provider: sec) | true |

## Data

| Name | Description |
| ---- | ----------- |
| files | Dictionary of URLs to SEC Schema Files (provider: sec) |
