---
title: Get the top ETF gainers
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
| `ETFGainers` | `ETFGainersQueryParams` | `ETFGainersData` |

### Import Statement

```python
from openbb_core.provider.standard_models. import (
ETFGainersData,
ETFGainersQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sort | str | Sort order. Possible values: 'asc', 'desc'. Default: 'desc'. | desc | True |
| limit | int | The number of data entries to return. | 10 | True |
| provider | Literal['wsj'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'wsj' if there is no default. | wsj | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| last_price | float | Last price. |
| percent_change | float | Percent change. |
| net_change | float | Net change. |
| volume | float | The trading volume. |
| date | date | The date of the data. |
</TabItem>

<TabItem value='wsj' label='wsj'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the entity. |
| last_price | float | Last price. |
| percent_change | float | Percent change. |
| net_change | float | Net change. |
| volume | float | The trading volume. |
| date | date | The date of the data. |
| bluegrass_channel | str | Bluegrass channel. |
| country | str | Country of the entity. |
| mantissa | int | Mantissa. |
| type | str | Type of the entity. |
| formatted_price | str | Formatted price. |
| formatted_volume | str | Formatted volume. |
| formatted_price_change | str | Formatted price change. |
| formatted_percent_change | str | Formatted percent change. |
| url | str | The source url. |
</TabItem>

</Tabs>
