---
title: "Options Unusual"
description: "Get the complete options chain for a ticker"
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

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (the underlying symbol) | None | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (the underlying symbol) | None | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. If no symbol is supplied, requests are only allowed for a single date. Use the start_date for the target date. Intrinio appears to have data beginning Feb/2022, but is unclear when it actually began. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. If a symbol is not supplied, do not include an end date. | None | True |
| trade_type | Literal['block', 'sweep', 'large'] | The type of unusual activity to query for. | None | True |
| sentiment | Literal['bullish', 'bearish', 'neutral'] | The sentiment type to query for. | None | True |
| min_value | Union[int, float] | The inclusive minimum total value for the unusual activity. | None | True |
| max_value | Union[int, float] | The inclusive maximum total value for the unusual activity. | None | True |
| limit | int | The number of data entries to return. A typical day for all symbols will yield 50-80K records. The API will paginate at 1000 records. The high default limit (100K) is to be able to reliably capture the most days. The high absolute limit (1.25M) is to allow for outlier days. Queries at the absolute limit will take a long time, and might be unreliable. Apply filters to improve performance. | 100000 | True |
| source | Literal['delayed', 'realtime'] | The source of the data. Either realtime or delayed. | delayed | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

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
| trade_timestamp | datetime | The datetime of order placement. |
| trade_type | Literal['block', 'sweep', 'large'] | The type of unusual trade. |
| sentiment | Literal['bullish', 'bearish', 'neutral'] | Bullish, Bearish, or Neutral Sentiment is estimated based on whether the trade was executed at the bid, ask, or mark price. |
| bid_at_execution | float | Bid price at execution. |
| ask_at_execution | float | Ask price at execution. |
| average_price | float | The average premium paid per option contract. |
| underlying_price_at_execution | float | Price of the underlying security at execution of trade. |
| total_size | int | The total number of contracts involved in a single transaction. |
| total_value | Union[int, float] | The aggregated value of all option contract premiums included in the trade. |
</TabItem>

</Tabs>

