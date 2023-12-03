---
title: Get the complete options chain for a ticker
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
| `OptionsUnusual` | `OptionsUnusualQueryParams` | `OptionsUnusualData` |

### Import Statement

```python
from openbb_core.provider.standard_models.options_unusual import (
OptionsUnusualData,
OptionsUnusualQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (the underlying symbol) | None | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (the underlying symbol) | None | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
| source | Literal['delayed', 'realtime'] | The source of the data. Either realtime or delayed. | delayed | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| underlying_symbol | str | Symbol representing the entity requested in the data. (the underlying symbol) |
| contract_symbol | str | Contract symbol for the option. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| underlying_symbol | str | Symbol representing the entity requested in the data. (the underlying symbol) |
| contract_symbol | str | Contract symbol for the option. |
| trade_type | str | The type of unusual trade. |
| sentiment | str | Bullish, Bearish, or Neutral Sentiment is estimated based on whether the trade was executed at the bid, ask, or mark price. |
| total_value | Union[int, float] | The aggregated value of all option contract premiums included in the trade. |
| total_size | int | The total number of contracts involved in a single transaction. |
| average_price | float | The average premium paid per option contract. |
| ask_at_execution | float | Ask price at execution. |
| bid_at_execution | float | Bid price at execution. |
| underlying_price_at_execution | float | Price of the underlying security at execution of trade. |
| timestamp | datetime | The UTC timestamp of order placement. |
</TabItem>

</Tabs>
