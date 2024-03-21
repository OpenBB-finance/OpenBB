---
title: "Available Indices"
description: "All indices available from a given provider"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `AvailableIndices` | `AvailableIndicesQueryParams` | `AvailableIndicesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.available_indices import (
AvailableIndicesData,
AvailableIndicesQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['cboe', 'fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['cboe', 'fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| use_cache | bool | When True, the Cboe Index directory will be cached for 24 hours. Set as False to bypass. | True | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['cboe', 'fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['cboe', 'fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| use_cache | bool | Whether to use a cached request. Index data is from a single JSON file, updated each day after close. It is cached for one day. To bypass, set to False. | True | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['cboe', 'fmp', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
| symbol | str | Symbol for the index. |
| description | str | Description for the index. Valid only for US indices. |
| data_delay | int | Data delay for the index. Valid only for US indices. |
| open_time | datetime.time | Opening time for the index. Valid only for US indices. |
| close_time | datetime.time | Closing time for the index. Valid only for US indices. |
| time_zone | str | Time zone for the index. Valid only for US indices. |
| tick_days | str | The trading days for the index. Valid only for US indices. |
| tick_frequency | str | The frequency of the index ticks. Valid only for US indices. |
| tick_period | str | The period of the index ticks. Valid only for US indices. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
| stock_exchange | str | Stock exchange where the index is listed. |
| exchange_short_name | str | Short name of the stock exchange where the index is listed. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
| symbol | str | The ticker symbol of the index. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
| code | str | ID code for keying the index in the OpenBB Terminal. |
| symbol | str | Symbol for the index. |
</TabItem>

</Tabs>

