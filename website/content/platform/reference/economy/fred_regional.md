---
title: "fred_regional"
description: "Query the Geo Fred API for regional economic data by series group"
keywords:
- economy
- fred_regional
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/fred_regional - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Query the Geo Fred API for regional economic data by series group.
The series group ID is found by using `fred_search` and the `series_id` parameter.


Examples
--------

```python
from openbb import obb
obb.economy.fred_regional(symbol='NYICLAIMS', provider='fred')
# With a date, time series data is returned.
obb.economy.fred_regional(symbol='NYICLAIMS', start_date='2021-01-01', end_date='2021-12-31', limit=10, provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): fred. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int | The number of data entries to return. | 100000 | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): fred. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int | The number of data entries to return. | 100000 | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| is_series_group | bool | When True, the symbol provided is for a series_group, else it is for a series ID. | False | True |
| region_type | Literal['bea', 'msa', 'frb', 'necta', 'state', 'country', 'county', 'censusregion'] | The type of regional data. Parameter is only valid when `is_series_group` is True. | None | True |
| season | Literal['SA', 'NSA', 'SSA'] | The seasonal adjustments to the data. Parameter is only valid when `is_series_group` is True. | NSA | True |
| units | str | The units of the data. This should match the units returned from searching by series ID. An incorrect field will not necessarily return an error. Parameter is only valid when `is_series_group` is True. | None | True |
| frequency | Literal['d', 'w', 'bw', 'm', 'q', 'sa', 'a', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem'] | Frequency aggregation to convert high frequency data to lower frequency.     Parameter is only valid when `is_series_group` is True.       a = Annual       sa= Semiannual       q = Quarterly       m = Monthly       w = Weekly       d = Daily       wef = Weekly, Ending Friday       weth = Weekly, Ending Thursday       wew = Weekly, Ending Wednesday       wetu = Weekly, Ending Tuesday       wem = Weekly, Ending Monday       wesu = Weekly, Ending Sunday       wesa = Weekly, Ending Saturday       bwew = Biweekly, Ending Wednesday       bwem = Biweekly, Ending Monday | None | True |
| aggregation_method | Literal['avg', 'sum', 'eop'] | A key that indicates the aggregation method used for frequency aggregation.     This parameter has no affect if the frequency parameter is not set.     Only valid when `is_series_group` is True.       avg = Average       sum = Sum       eop = End of Period | avg | True |
| transform | Literal['lin', 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log'] | Transformation type. Only valid when `is_series_group` is True.       lin = Levels (No transformation)       chg = Change       ch1 = Change from Year Ago       pch = Percent Change       pc1 = Percent Change from Year Ago       pca = Compounded Annual Rate of Change       cch = Continuously Compounded Rate of Change       cca = Continuously Compounded Annual Rate of Change       log = Natural Log | lin | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : FredRegional
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
| region | str | The name of the region. |
| code | Union[str, int] | The code of the region. |
| value | Union[int, float] | The obersvation value. The units are defined in the search results by series ID. |
| series_id | str | The individual series ID for the region. |
</TabItem>

</Tabs>

