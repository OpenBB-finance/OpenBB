---
title: EquitySearch
description: Equity Search
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EquitySearch` | `EquitySearchQueryParams` | `EquitySearchData` |

### Import Statement

```python
from openbb_provider.standard_models.equity_search import (
EquitySearchData,
EquitySearchQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe', 'sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe', 'sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| is_fund | bool | Whether to direct the search to the list of mutual funds and ETFs. | False | True |
| use_cache | bool | Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days. | True | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| dpm_name | str | Name of the primary market maker. |
| post_station | str | Post and station location on the CBOE trading floor. |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| cik | str | Central Index Key |
</TabItem>

</Tabs>

