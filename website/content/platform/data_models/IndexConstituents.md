---
title: "Index Constituents"
description: "Index Constituents"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `IndexConstituents` | `IndexConstituentsQueryParams` | `IndexConstituentsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.index_constituents import (
IndexConstituentsData,
IndexConstituentsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['cboe', 'fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| use_cache | bool | Whether to use a cached request. Index data is from a single JSON file, updated each day after close. It is cached for one day. To bypass, set to False. | True | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
| security_type | str | The type of security represented. |
| last_price | float | Last price for the symbol. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | Change in price. |
| change_percent | float | Change in price as a normalized percentage. |
| tick | str | Whether the last sale was an up or down tick. |
| last_trade_time | datetime | Last trade timestamp for the symbol. |
| asset_type | str | Type of asset. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
| sector | str | Sector the constituent company in the index belongs to. |
| sub_sector | str | Sub-sector the constituent company in the index belongs to. |
| headquarter | str | Location of the headquarter of the constituent company in the index. |
| date_first_added | Union[str, date] | Date the constituent company was added to the index. |
| cik | int | Central Index Key (CIK) for the requested entity. |
| founded | Union[str, date] | Founding year of the constituent company in the index. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
| market_value | float | The quoted market value of the asset. |
</TabItem>

</Tabs>

