---
title: "upcoming_release_days"
description: "Learn how to get upcoming release days for equity discovery using the  OBB object and the seeking alpha provider. Understand the parameters and data returned  by the API."
keywords:
- upcoming release days
- equity discovery
- provider
- seeking alpha
- parameters
- returns
- data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/discovery/upcoming_release_days - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get upcoming earnings release dates.


Examples
--------

```python
from openbb import obb
obb.equity.discovery.upcoming_release_days(provider='seeking_alpha')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['seeking_alpha'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'seeking_alpha' if there is no default. | seeking_alpha | True |
</TabItem>

<TabItem value='seeking_alpha' label='seeking_alpha'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['seeking_alpha'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'seeking_alpha' if there is no default. | seeking_alpha | True |
| limit | int | The number of data entries to return.In this case, the number of lookahead days. | 10 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : UpcomingReleaseDays
        Serializable results.
    provider : Literal['seeking_alpha']
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
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | The full name of the asset. |
| exchange | str | The exchange the asset is traded on. |
| release_time_type | str | The type of release time. |
| release_date | date | The date of the release. |
</TabItem>

<TabItem value='seeking_alpha' label='seeking_alpha'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | The full name of the asset. |
| exchange | str | The exchange the asset is traded on. |
| release_time_type | str | The type of release time. |
| release_date | date | The date of the release. |
| sector_id | int | The sector ID of the asset. |
</TabItem>

</Tabs>

