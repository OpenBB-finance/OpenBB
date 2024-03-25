---
title: "Lbma Fixing"
description: "Daily LBMA Fixing Prices in USD/EUR/GBP"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `LbmaFixing` | `LbmaFixingQueryParams` | `LbmaFixingData` |

### Import Statement

```python
from openbb_core.provider.standard_models.lbma_fixing import (
LbmaFixingData,
LbmaFixingQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | Literal['gold', 'silver'] | The metal to get price fixing rates for. | gold | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as difference, percent change, cumulative, or normalize. | None | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | None | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| asset | Literal['gold', 'silver'] | The metal to get price fixing rates for. | gold | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| transform | Literal['diff', 'rdiff', 'cumul', 'normalize'] | Transform the data as difference, percent change, cumulative, or normalize. | None | True |
| collapse | Literal['daily', 'weekly', 'monthly', 'quarterly', 'annual'] | Collapse the frequency of the time series. | None | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| usd_am | float | AM fixing price in USD. |
| usd_pm | float | PM fixing price in USD. |
| gbp_am | float | AM fixing price in GBP. |
| gbp_pm | float | PM fixing price in GBP. |
| euro_am | float | AM fixing price in EUR. |
| euro_pm | float | PM fixing price in EUR. |
| usd | float | Daily fixing price in USD. |
| gbp | float | Daily fixing price in GBP. |
| eur | float | Daily fixing price in EUR. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| usd_am | float | AM fixing price in USD. |
| usd_pm | float | PM fixing price in USD. |
| gbp_am | float | AM fixing price in GBP. |
| gbp_pm | float | PM fixing price in GBP. |
| euro_am | float | AM fixing price in EUR. |
| euro_pm | float | PM fixing price in EUR. |
| usd | float | Daily fixing price in USD. |
| gbp | float | Daily fixing price in GBP. |
| eur | float | Daily fixing price in EUR. |
</TabItem>

</Tabs>

