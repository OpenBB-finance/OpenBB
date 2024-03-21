---
title: "cpi"
description: "Get Consumer Price Index (CPI) data for various countries and calculate  inflation measurements. This economic indicator provides insights into the growth  rate of prices on a monthly, quarterly, and annual basis. Harmonized CPI data is  also available. Specify the start and end dates for the desired data range. The  data provider and metadata information are included in the results."
keywords:
- Consumer Price Index (CPI) Data
- CPI data
- CPI calculation
- inflation measurement
- economic indicator
- country-wise CPI data
- growth rate
- monthly CPI
- quarterly CPI
- annual CPI
- harmonized CPI
- start date
- end date
- data provider
- metadata info
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/cpi - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Consumer Price Index (CPI).  Returns either the rescaled index value, or a rate of change (inflation).


Examples
--------

```python
from openbb import obb
obb.economy.cpi(country='japan,china,turkey', provider='fred')
# Use the `units` parameter to define the reference period for the change in values.
obb.economy.cpi(country='united_states,united_kingdom', units='growth_previous', provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | Union[str, List[str]] | The country to get data. Multiple items allowed for provider(s): fred. |  | False |
| units | Literal['growth_previous', 'growth_same', 'index_2015'] | The unit of measurement for the data.   Options:   - `growth_previous`: Percent growth from the previous period.    If monthly data, this is month-over-month, etc   - `growth_same`: Percent growth from the same period in the previous year.    If looking at monthly data, this would be year-over-year, etc.   - `index_2015`: Rescaled index value, such that the value in 2015 is 100. | growth_same | True |
| frequency | Literal['monthly', 'quarter', 'annual'] | The frequency of the data.   Options: `monthly`, `quarter`, and `annual`. | monthly | True |
| harmonized | bool | Whether you wish to obtain harmonized data. | False | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | Union[str, List[str]] | The country to get data. Multiple items allowed for provider(s): fred. |  | False |
| units | Literal['growth_previous', 'growth_same', 'index_2015'] | The unit of measurement for the data.   Options:   - `growth_previous`: Percent growth from the previous period.    If monthly data, this is month-over-month, etc   - `growth_same`: Percent growth from the same period in the previous year.    If looking at monthly data, this would be year-over-year, etc.   - `index_2015`: Rescaled index value, such that the value in 2015 is 100. | growth_same | True |
| frequency | Literal['monthly', 'quarter', 'annual'] | The frequency of the data.   Options: `monthly`, `quarter`, and `annual`. | monthly | True |
| harmonized | bool | Whether you wish to obtain harmonized data. | False | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : ConsumerPriceIndex
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
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

</Tabs>

