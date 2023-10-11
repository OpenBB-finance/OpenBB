---
title: Stock Search
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `StockSearch` | `StockSearchQueryParams` | `StockSearchData` |

### Import Statement

```python
from openbb_provider.standard_models.stock_search import (
StockSearchData,
StockSearchQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| ticker | bool | Whether to search by ticker symbol. | False | True |
| provider | Union[Literal['cboe']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| name | str | Name of the company. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| name | str | Name of the company. |
| dpm_name | Union[str] | Name of the primary market maker. |
| post_station | Union[str] | Post and station location on the CBOE trading floor. |
</TabItem>

</Tabs>

