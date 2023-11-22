---
title: Index Search
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
| `IndexSearch` | `IndexSearchQueryParams` | `IndexSearchData` |

### Import Statement

```python
from openbb_core.provider.standard_models.index_search import (
IndexSearchData,
IndexSearchQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| europe | bool | Filter for European indices. False for US indices. | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the index. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the index. |
| isin | str | ISIN code for the index. Valid only for European indices. |
| region | str | Region for the index. Valid only for European indices |
| description | str | Description for the index. |
| data_delay | int | Data delay for the index. Valid only for US indices. |
| currency | str | Currency for the index. |
| time_zone | str | Time zone for the index. Valid only for US indices. |
| open_time | datetime.time | Opening time for the index. Valid only for US indices. |
| close_time | datetime.time | Closing time for the index. Valid only for US indices. |
| tick_days | str | The trading days for the index. Valid only for US indices. |
| tick_frequency | str | Tick frequency for the index. Valid only for US indices. |
| tick_period | str | Tick period for the index. Valid only for US indices. |
</TabItem>

</Tabs>
