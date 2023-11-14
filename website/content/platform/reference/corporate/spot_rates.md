---
title: spot_rates
description: Learn about spot rates and how they are used to calculate the yield on
  a bond. Understand the concept of discounting and its application in evaluating
  pension liabilities. Explore the parameters needed to query and retrieve spot rate
  data. Get the serializable results, provider information, warnings, chart, and metadata
  associated with the query. Access the spot rate data including the date and rate.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Spot Rates.

The spot rates for any maturity is the yield on a bond that provides a single payment at that maturity.
This is a zero coupon bond.
Because each spot rate pertains to a single cashflow, it is the relevant interest rate
concept for discounting a pension liability at the same maturity.

```python wordwrap
obb.fixedincome.corporate.spot_rates(start_date: Union[date, str] = None, end_date: Union[date, str] = None, maturity: List[float] = [10.0], category: List[Literal[list]] = ['spot_rate'], provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | List[float] | The maturities in years. | [10.0] | True |
| category | List[Literal['par_yield', 'spot_rate']] | The category. | ['spot_rate'] | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[SpotRate]
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
| date | date | The date of the data. |
| rate | float | Spot Rate. |
</TabItem>

</Tabs>

