---
title: "historical_attributes"
description: "Get the historical values of a data tag from Intrinio"
keywords:
- equity
- fundamental
- historical_attributes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/historical_attributes - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the historical values of a data tag from Intrinio.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.historical_attributes(symbol='AAPL', tag='ebitda', provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): intrinio. |  | False |
| tag | Union[str, List[str]] | Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| frequency | Literal['daily', 'weekly', 'monthly', 'quarterly', 'yearly'] | The frequency of the data. | yearly | True |
| limit | int | The number of data entries to return. | 1000 | True |
| tag_type | str | Filter by type, when applicable. | None | True |
| sort | Literal['asc', 'desc'] | Sort order. | desc | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): intrinio. |  | False |
| tag | Union[str, List[str]] | Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| frequency | Literal['daily', 'weekly', 'monthly', 'quarterly', 'yearly'] | The frequency of the data. | yearly | True |
| limit | int | The number of data entries to return. | 1000 | True |
| tag_type | str | Filter by type, when applicable. | None | True |
| sort | Literal['asc', 'desc'] | Sort order. | desc | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : HistoricalAttributes
        Serializable results.
    provider : Literal['intrinio']
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
| symbol | str | Symbol representing the entity requested in the data. |
| tag | str | Tag name for the fetched data. |
| value | float | The value of the data. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| symbol | str | Symbol representing the entity requested in the data. |
| tag | str | Tag name for the fetched data. |
| value | float | The value of the data. |
</TabItem>

</Tabs>

