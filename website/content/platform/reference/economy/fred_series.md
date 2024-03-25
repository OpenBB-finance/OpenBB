---
title: "fred_series"
description: "Get data by series ID from FRED"
keywords:
- economy
- fred_series
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/fred_series - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get data by series ID from FRED.


Examples
--------

```python
from openbb import obb
obb.economy.fred_series(symbol='NFCI', provider='fred')
# Multiple series can be passed in as a list.
obb.economy.fred_series(symbol='NFCI,STLFSI4', provider='fred')
# Use the `transform` parameter to transform the data as change, log, or percent change.
obb.economy.fred_series(symbol='CBBTCUSD', transform=pc1, provider='fred')
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
| provider | Literal['fred', 'intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): fred. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int | The number of data entries to return. | 100000 | True |
| provider | Literal['fred', 'intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| frequency | Literal[None, 'a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem'] | Frequency aggregation to convert high frequency data to lower frequency.       None = No change       a = Annual       q = Quarterly       m = Monthly       w = Weekly       d = Daily       wef = Weekly, Ending Friday       weth = Weekly, Ending Thursday       wew = Weekly, Ending Wednesday       wetu = Weekly, Ending Tuesday       wem = Weekly, Ending Monday       wesu = Weekly, Ending Sunday       wesa = Weekly, Ending Saturday       bwew = Biweekly, Ending Wednesday       bwem = Biweekly, Ending Monday | None | True |
| aggregation_method | Literal[None, 'avg', 'sum', 'eop'] | A key that indicates the aggregation method used for frequency aggregation.     This parameter has no affect if the frequency parameter is not set.       avg = Average       sum = Sum       eop = End of Period | eop | True |
| transform | Literal[None, 'chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log'] | Transformation type       None = No transformation       chg = Change       ch1 = Change from Year Ago       pch = Percent Change       pc1 = Percent Change from Year Ago       pca = Compounded Annual Rate of Change       cch = Continuously Compounded Rate of Change       cca = Continuously Compounded Annual Rate of Change       log = Natural Log | None | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): fred. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | int | The number of data entries to return. | 100000 | True |
| provider | Literal['fred', 'intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| all_pages | bool | Returns all pages of data from the API call at once. | False | True |
| sleep | float | Time to sleep between requests to avoid rate limiting. | 1.0 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : FredSeries
        Serializable results.
    provider : Literal['fred', 'intrinio']
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

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| value | float | Value of the index. |
</TabItem>

</Tabs>

