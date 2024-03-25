---
title: "spot_rates"
description: "Learn about spot rates and how they are used to calculate the yield on  a bond. Understand the concept of discounting and its application in evaluating  pension liabilities. Explore the parameters needed to query and retrieve spot rate  data. Get the serializable results, provider information, warnings, chart, and metadata  associated with the query. Access the spot rate data including the date and rate."
keywords:
- spot rates
- yield
- bond
- zero coupon bond
- interest rate
- discounting
- pension liability
- maturities
- query
- results
- provider
- warnings
- chart
- metadata
- data
- date
- rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/corporate/spot_rates - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Spot Rates.

The spot rates for any maturity is the yield on a bond that provides a single payment at that maturity.
This is a zero coupon bond.
Because each spot rate pertains to a single cashflow, it is the relevant interest rate
concept for discounting a pension liability at the same maturity.


Examples
--------

```python
from openbb import obb
obb.fixedincome.corporate.spot_rates(provider='fred')
obb.fixedincome.corporate.spot_rates(maturity='10,20,30,50', provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Union[Union[float, str], List[Union[float, str]]] | Maturities in years. Multiple items allowed for provider(s): fred. | 10.0 | True |
| category | Union[str, List[str]] | Rate category. Options: spot_rate, par_yield. Multiple items allowed for provider(s): fred. | spot_rate | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Union[Union[float, str], List[Union[float, str]]] | Maturities in years. Multiple items allowed for provider(s): fred. | 10.0 | True |
| category | Union[str, List[str]] | Rate category. Options: spot_rate, par_yield. Multiple items allowed for provider(s): fred. | spot_rate | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : SpotRate
        Serializable results.
    provider : Literal['fred']
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
| date | date | The date of the data. |
| rate | float | Spot Rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | Spot Rate. |
</TabItem>

</Tabs>

