---
title: Fuzzy search for Industry Titles, Reporting Office, and SIC Codes
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `SicSearch` | `SicSearchQueryParams` | `SicSearchData` |

### Import Statement

```python
from openbb_core.provider.standard_models. import (
SicSearchData,
SicSearchQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
| use_cache | bool | Whether to use the cache or not. The full list will be cached for seven days if True. | True | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| sic | int | Sector Industrial Code (SIC) |
| industry | str | Industry title. |
| office | str | Reporting office within the Corporate Finance Office |
</TabItem>

</Tabs>
