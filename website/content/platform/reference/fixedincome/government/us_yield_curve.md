---
title: "us_yield_curve"
description: "Learn about the US Yield Curve and how to retrieve United States yield  curve data using the OBB.fixedincome.government.us_yield_curve function. Explore  parameters like date, inflation adjustment, and provider. Understand the returned  results, including the chart, metadata, and warnings. Discover the data structure,  including maturity and rate."
keywords:
- US Yield Curve
- United States yield curve
- yield curve
- government bonds
- fixed income
- rates
- inflation adjusted
- FRED provider
- data
- maturity
- treasury rate
- rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/government/us_yield_curve - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

US Yield Curve. Get United States yield curve.


Examples
--------

```python
from openbb import obb
obb.fixedincome.government.us_yield_curve(provider='fred')
obb.fixedincome.government.us_yield_curve(inflation_adjusted=True, provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. Defaults to the most recent FRED entry. | None | True |
| inflation_adjusted | bool | Get inflation adjusted rates. | False | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. Defaults to the most recent FRED entry. | None | True |
| inflation_adjusted | bool | Get inflation adjusted rates. | False | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : USYieldCurve
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
| maturity | float | Maturity of the treasury rate in years. |
| rate | float | Associated rate given in decimal form (0.05 is 5%) |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| maturity | float | Maturity of the treasury rate in years. |
| rate | float | Associated rate given in decimal form (0.05 is 5%) |
</TabItem>

</Tabs>

