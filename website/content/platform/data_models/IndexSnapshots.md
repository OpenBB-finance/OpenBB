---
title: "Index Snapshots"
description: "Index Snapshots"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `IndexSnapshots` | `IndexSnapshotsQueryParams` | `IndexSnapshotsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.index_snapshots import (
IndexSnapshotsData,
IndexSnapshotsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| region | str | The region of focus for the data - i.e., us, eu. | us | True |
| provider | Literal['cboe', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| region | str | The region of focus for the data - i.e., us, eu. | us | True |
| provider | Literal['cboe', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| region | str | The region of focus for the data - i.e., us, eu. | us | True |
| provider | Literal['cboe', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
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
| name | str | Name of the index. |
| currency | str | Currency of the index. |
| price | float | Current price of the index. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | Change in value of the index. |
| change_percent | float | Change, in normalized percentage points, of the index. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the index. |
| currency | str | Currency of the index. |
| price | float | Current price of the index. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | Change in value of the index. |
| change_percent | float | Change, in normalized percentage points, of the index. |
| bid | float | Current bid price. |
| ask | float | Current ask price. |
| last_trade_time | datetime | Last trade timestamp for the symbol. |
| status | str | Status of the market, open or closed. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the index. |
| currency | str | Currency of the index. |
| price | float | Current price of the index. |
| open | float | The open price. |
| high | float | The high price. |
| low | float | The low price. |
| close | float | The close price. |
| volume | int | The trading volume. |
| prev_close | float | The previous close price. |
| change | float | Change in value of the index. |
| change_percent | float | Change, in normalized percentage points, of the index. |
| year_high | float | The 52-week high of the index. |
| year_low | float | The 52-week low of the index. |
| return_mtd | float | The month-to-date return of the index, as a normalized percent. |
| return_qtd | float | The quarter-to-date return of the index, as a normalized percent. |
| return_ytd | float | The year-to-date return of the index, as a normalized percent. |
| total_market_value | float | The total quoted market value of the index. |
| number_of_constituents | int | The number of constituents in the index. |
| constituent_average_market_value | float | The average quoted market value of the index constituents. |
| constituent_median_market_value | float | The median quoted market value of the index constituents. |
| constituent_top10_market_value | float | The sum of the top 10 quoted market values of the index constituents. |
| constituent_largest_market_value | float | The largest quoted market value of the index constituents. |
| constituent_largest_weight | float | The largest weight of the index constituents, as a normalized percent. |
| constituent_smallest_market_value | float | The smallest quoted market value of the index constituents. |
| constituent_smallest_weight | float | The smallest weight of the index constituents, as a normalized percent. |
</TabItem>

</Tabs>

