---
title: "money_measures"
description: "Money Measures (M1/M2 and components)"
keywords:
- economy
- money_measures
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/money_measures - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Money Measures (M1/M2 and components). The Federal Reserve publishes as part of the H.6 Release.


Examples
--------

```python
from openbb import obb
obb.economy.money_measures(provider='federal_reserve')
obb.economy.money_measures(adjusted=False, provider='federal_reserve')
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

## Returns

```python wordwrap
OBBject
    results : MoneyMeasures
        Serializable results.
    provider : Literal['federal_reserve']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

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

