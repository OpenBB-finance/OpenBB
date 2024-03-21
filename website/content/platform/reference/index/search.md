---
title: "search"
description: "Learn how to perform index search and retrieve index data using this  Python API. Understand the different parameters and their defaults, and get detailed  information about index symbols, names, and additional attributes such as ISIN code,  region, description, currency, and trading times."
keywords:
- index search
- search indices
- Python search query
- index data
- index symbol
- index name
- European indices
- US indices
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="index/search - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Filters indices for rows containing the query.


Examples
--------

```python
from openbb import obb
obb.index.search(provider='cboe')
obb.index.search(query='SPX', provider='cboe')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

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
| use_cache | bool | When True, the Cboe Index directory will be cached for 24 hours. Set as False to bypass. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : IndexSearch
        Serializable results.
    provider : Literal['cboe']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

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

