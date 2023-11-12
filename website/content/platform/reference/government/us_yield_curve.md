---
title: us_yield_curve
description: Learn about the US Yield Curve and how to retrieve United States yield
  curve data using the OBB.fixedincome.government.us_yield_curve function. Explore
  parameters like date, inflation adjustment, and provider. Understand the returned
  results, including the chart, metadata, and warnings. Discover the data structure,
  including maturity and rate.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

US Yield Curve. Get United States yield curve.

```python wordwrap
obb.fixedincome.government.us_yield_curve(date: date = None, inflation_adjusted: bool = False, provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | date | A specific date to get data for. Defaults to the most recent FRED entry. | None | True |
| inflation_adjusted | bool | Get inflation adjusted rates. | False | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[USYieldCurve]
        Serializable results.

    provider : Optional[Literal['fred']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| maturity | float | Maturity of the treasury rate in years. |
| rate | float | Associated rate given in decimal form (0.05 is 5%) |
</TabItem>

</Tabs>

