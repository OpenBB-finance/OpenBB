---
title: Get the most-recent filings submitted to the SEC
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
| `DiscoveryFilings` | `DiscoveryFilingsQueryParams` | `DiscoveryFilingsData` |

### Import Statement

```python
from openbb_core.provider.standard_models. import (
DiscoveryFilingsData,
DiscoveryFilingsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| form_type | str | Fuzzy filter by form type. E.g. 10-K, 10, 8, 6-K, etc. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| form_type | str | Fuzzy filter by form type. E.g. 10-K, 10, 8, 6-K, etc. | None | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| is_done | Literal['true', 'false'] | Flag for whether or not the filing is done. | None | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| timestamp | datetime | The timestamp from when the filing was accepted. |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | The CIK of the filing |
| title | str | The title of the filing |
| form_type | str | The form type of the filing |
| url | str | The URL of the filing |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| timestamp | datetime | The timestamp from when the filing was accepted. |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | The CIK of the filing |
| title | str | The title of the filing |
| form_type | str | The form type of the filing |
| url | str | The URL of the filing |
| is_done | Literal['True', 'False'] | Whether or not the filing is done. |
</TabItem>

</Tabs>
