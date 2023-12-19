---
title: ice_bofa
description: Learn about ICE BofA US Corporate Bond Indices, including the ICE BofA
  US Corporate Index and parameters for the `obb.fixedincome.corporate.ice_bofa` function.
  Find out how to retrieve historical data and explore the available categories and
  areas.
keywords:
- ICE BofA US Corporate Bond Indices
- ICE BofA US Corporate Index
- US dollar denominated investment grade corporate debt
- Moody's
- S&P
- Fitch
- investment grade rating
- final maturity
- rebalance date
- fixed coupon schedule
- minimum amount outstanding
- US Corporate Master Index
- start date
- end date
- index type
- provider
- fred
- category
- area
- grade
- options
- returns
- results
- warnings
- chart
- metadata
- data
- rate
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

ICE BofA US Corporate Bond Indices.

The ICE BofA US Corporate Index tracks the performance of US dollar denominated investment grade corporate debt
publicly issued in the US domestic market. Qualifying securities must have an investment grade rating (based on an
average of Moody’s, S&P and Fitch), at least 18 months to final maturity at the time of issuance, at least one year
remaining term to final maturity as of the rebalance date, a fixed coupon schedule and a minimum amount
outstanding of $250 million. The ICE BofA US Corporate Index is a component of the US Corporate Master Index.

```python wordwrap
obb.fixedincome.corporate.ice_bofa(start_date: Union[date, str] = None, end_date: Union[date, str] = None, index_type: Literal[str] = yield, provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| index_type | Literal['yield', 'yield_to_worst', 'total_return', 'spread'] | The type of series. | yield | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| index_type | Literal['yield', 'yield_to_worst', 'total_return', 'spread'] | The type of series. | yield | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| category | Literal['all', 'duration', 'eur', 'usd'] | The type of category. | all | True |
| area | Literal['asia', 'emea', 'eu', 'ex_g10', 'latin_america', 'us'] | The type of area. | us | True |
| grade | Literal['a', 'aa', 'aaa', 'b', 'bb', 'bbb', 'ccc', 'crossover', 'high_grade', 'high_yield', 'non_financial', 'non_sovereign', 'private_sector', 'public_sector'] | The type of grade. | non_sovereign | True |
| options | bool | Whether to include options in the results. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[ICEBofA]
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
| rate | float | ICE BofA US Corporate Bond Indices Rate. |
</TabItem>

</Tabs>

