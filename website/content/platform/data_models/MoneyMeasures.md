---
title: "Money Measures"
description: "Money Measures (M1/M2 and components)"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `MoneyMeasures` | `MoneyMeasuresQueryParams` | `MoneyMeasuresData` |

### Import Statement

```python
from openbb_core.provider.standard_models.money_measures import (
MoneyMeasuresData,
MoneyMeasuresQueryParams,
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
| adjusted | bool | Whether to return seasonally adjusted data. | True | True |
| provider | Literal['federal_reserve'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'federal_reserve' if there is no default. | federal_reserve | True |
</TabItem>

<TabItem value='federal_reserve' label='federal_reserve'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| adjusted | bool | Whether to return seasonally adjusted data. | True | True |
| provider | Literal['federal_reserve'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'federal_reserve' if there is no default. | federal_reserve | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| month | date | The date of the data. |
| M1 | float | Value of the M1 money supply in billions. |
| M2 | float | Value of the M2 money supply in billions. |
| currency | float | Value of currency in circulation in billions. |
| demand_deposits | float | Value of demand deposits in billions. |
| retail_money_market_funds | float | Value of retail money market funds in billions. |
| other_liquid_deposits | float | Value of other liquid deposits in billions. |
| small_denomination_time_deposits | float | Value of small denomination time deposits in billions. |
</TabItem>

<TabItem value='federal_reserve' label='federal_reserve'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| month | date | The date of the data. |
| M1 | float | Value of the M1 money supply in billions. |
| M2 | float | Value of the M2 money supply in billions. |
| currency | float | Value of currency in circulation in billions. |
| demand_deposits | float | Value of demand deposits in billions. |
| retail_money_market_funds | float | Value of retail money market funds in billions. |
| other_liquid_deposits | float | Value of other liquid deposits in billions. |
| small_denomination_time_deposits | float | Value of small denomination time deposits in billions. |
</TabItem>

</Tabs>

