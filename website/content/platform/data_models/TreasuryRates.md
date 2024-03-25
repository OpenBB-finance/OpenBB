---
title: "Treasury Rates"
description: "Government Treasury Rates"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `TreasuryRates` | `TreasuryRatesQueryParams` | `TreasuryRatesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.treasury_rates import (
TreasuryRatesData,
TreasuryRatesQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['federal_reserve', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'federal_reserve' if there is no default. | federal_reserve | True |
</TabItem>

<TabItem value='federal_reserve' label='federal_reserve'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['federal_reserve', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'federal_reserve' if there is no default. | federal_reserve | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['federal_reserve', 'fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'federal_reserve' if there is no default. | federal_reserve | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| week_4 | float | 4 week Treasury bills rate (secondary market). |
| month_1 | float | 1 month Treasury rate. |
| month_2 | float | 2 month Treasury rate. |
| month_3 | float | 3 month Treasury rate. |
| month_6 | float | 6 month Treasury rate. |
| year_1 | float | 1 year Treasury rate. |
| year_2 | float | 2 year Treasury rate. |
| year_3 | float | 3 year Treasury rate. |
| year_5 | float | 5 year Treasury rate. |
| year_7 | float | 7 year Treasury rate. |
| year_10 | float | 10 year Treasury rate. |
| year_20 | float | 20 year Treasury rate. |
| year_30 | float | 30 year Treasury rate. |
</TabItem>

<TabItem value='federal_reserve' label='federal_reserve'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| week_4 | float | 4 week Treasury bills rate (secondary market). |
| month_1 | float | 1 month Treasury rate. |
| month_2 | float | 2 month Treasury rate. |
| month_3 | float | 3 month Treasury rate. |
| month_6 | float | 6 month Treasury rate. |
| year_1 | float | 1 year Treasury rate. |
| year_2 | float | 2 year Treasury rate. |
| year_3 | float | 3 year Treasury rate. |
| year_5 | float | 5 year Treasury rate. |
| year_7 | float | 7 year Treasury rate. |
| year_10 | float | 10 year Treasury rate. |
| year_20 | float | 20 year Treasury rate. |
| year_30 | float | 30 year Treasury rate. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| week_4 | float | 4 week Treasury bills rate (secondary market). |
| month_1 | float | 1 month Treasury rate. |
| month_2 | float | 2 month Treasury rate. |
| month_3 | float | 3 month Treasury rate. |
| month_6 | float | 6 month Treasury rate. |
| year_1 | float | 1 year Treasury rate. |
| year_2 | float | 2 year Treasury rate. |
| year_3 | float | 3 year Treasury rate. |
| year_5 | float | 5 year Treasury rate. |
| year_7 | float | 7 year Treasury rate. |
| year_10 | float | 10 year Treasury rate. |
| year_20 | float | 20 year Treasury rate. |
| year_30 | float | 30 year Treasury rate. |
</TabItem>

</Tabs>

