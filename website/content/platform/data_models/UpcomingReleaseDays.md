---
title: Get upcoming release days
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
| `UpcomingReleaseDays` | `UpcomingReleaseDaysQueryParams` | `UpcomingReleaseDaysData` |

### Import Statement

```python
from openbb_core.provider.standard_models.upcoming_release_days import (
UpcomingReleaseDaysData,
UpcomingReleaseDaysQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['seeking_alpha'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'seeking_alpha' if there is no default. | seeking_alpha | True |
</TabItem>

<TabItem value='seeking_alpha' label='seeking_alpha'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['seeking_alpha'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'seeking_alpha' if there is no default. | seeking_alpha | True |
| limit | int | The number of data entries to return.In this case, the number of lookahead days. | 10 | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | The full name of the asset. |
| exchange | str | The exchange the asset is traded on. |
| release_time_type | str | The type of release time. |
| release_date | date | The date of the release. |
</TabItem>

<TabItem value='seeking_alpha' label='seeking_alpha'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | The full name of the asset. |
| exchange | str | The exchange the asset is traded on. |
| release_time_type | str | The type of release time. |
| release_date | date | The date of the release. |
| sector_id | int | The sector ID of the asset. |
</TabItem>

</Tabs>
