---
title: European Index Constituents
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
| `EuropeanIndexConstituents` | `EuropeanIndexConstituentsQueryParams` | `EuropeanIndexConstituentsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.european_index_constituents import (
EuropeanIndexConstituentsData,
EuropeanIndexConstituentsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['cboe'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. The symbol is the constituent company in the index. |
| price | float | Current price of the constituent company in the index. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | float | The trading volume. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. The symbol is the constituent company in the index. |
| price | float | Current price of the constituent company in the index. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | float | The trading volume. |
| prev_close | float | Previous closing  price. |
| change | float | Change in price. |
| change_percent | float | Change in price as a percentage. |
| tick | str | Whether the last sale was an up or down tick. |
| last_trade_timestamp | datetime | Last trade timestamp for the symbol. |
| exchange_id | int | The Exchange ID number. |
| seqno | int | Sequence number of the last trade on the tape. |
| asset_type | str | Type of asset. |
</TabItem>

</Tabs>
