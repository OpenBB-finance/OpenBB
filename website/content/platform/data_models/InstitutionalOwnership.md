---
title: Institutional Ownership
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
| `InstitutionalOwnership` | `InstitutionalOwnershipQueryParams` | `InstitutionalOwnershipData` |

### Import Statement

```python
from openbb_core.provider.standard_models.institutional_ownership import (
InstitutionalOwnershipData,
InstitutionalOwnershipQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| include_current_quarter | bool | Include current quarter data. | False | True |
| date | date | A specific date to get data for. | None | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| cik | str | CIK of the company. |
| date | date | The date of the data. |
| investors_holding | int | Number of investors holding the stock. |
| last_investors_holding | int | Number of investors holding the stock in the last quarter. |
| investors_holding_change | int | Change in the number of investors holding the stock. |
| number_of_13f_shares | int | Number of 13F shares. |
| last_number_of_13f_shares | int | Number of 13F shares in the last quarter. |
| number_of_13f_shares_change | int | Change in the number of 13F shares. |
| total_invested | float | Total amount invested. |
| last_total_invested | float | Total amount invested in the last quarter. |
| total_invested_change | float | Change in the total amount invested. |
| ownership_percent | float | Ownership percent. |
| last_ownership_percent | float | Ownership percent in the last quarter. |
| ownership_percent_change | float | Change in the ownership percent. |
| new_positions | int | Number of new positions. |
| last_new_positions | int | Number of new positions in the last quarter. |
| new_positions_change | int | Change in the number of new positions. |
| increased_positions | int | Number of increased positions. |
| last_increased_positions | int | Number of increased positions in the last quarter. |
| increased_positions_change | int | Change in the number of increased positions. |
| closed_positions | int | Number of closed positions. |
| last_closed_positions | int | Number of closed positions in the last quarter. |
| closed_positions_change | int | Change in the number of closed positions. |
| reduced_positions | int | Number of reduced positions. |
| last_reduced_positions | int | Number of reduced positions in the last quarter. |
| reduced_positions_change | int | Change in the number of reduced positions. |
| total_calls | int | Total number of call options contracts traded for Apple Inc. on the specified date. |
| last_total_calls | int | Total number of call options contracts traded for Apple Inc. on the previous reporting date. |
| total_calls_change | int | Change in the total number of call options contracts traded between the current and previous reporting dates. |
| total_puts | int | Total number of put options contracts traded for Apple Inc. on the specified date. |
| last_total_puts | int | Total number of put options contracts traded for Apple Inc. on the previous reporting date. |
| total_puts_change | int | Change in the total number of put options contracts traded between the current and previous reporting dates. |
| put_call_ratio | float | Put-call ratio, which is the ratio of the total number of put options to call options traded on the specified date. |
| last_put_call_ratio | float | Put-call ratio on the previous reporting date. |
| put_call_ratio_change | float | Change in the put-call ratio between the current and previous reporting dates. |
</TabItem>

</Tabs>
