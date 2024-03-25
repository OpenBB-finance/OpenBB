---
title: "cot_search"
description: "Learn about curated Commitment of Traders Reports series information  and how to perform a search for specific data. Find details on the parameters,  data returned, and available CFTC codes."
keywords:
- Commitment of Traders Reports
- curated COT Reports series
- CFTC Code
- underlying asset
- search query
- provider
- results
- warnings
- chart object
- metadata info
- CFTC
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="regulators/cftc/cot_search - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Curated Commitment of Traders Reports.

Search a list of curated Commitment of Traders Reports series information.


Examples
--------

```python
from openbb import obb
obb.regulators.cftc.cot_search(provider='nasdaq')
obb.regulators.cftc.cot_search(query='gold', provider='nasdaq')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| use_cache | bool | Whether or not to use cache. If True, cache will store for seven days. | True | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| use_cache | bool | Whether or not to use cache. If True, cache will store for seven days. | True | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : COTSearch
        Serializable results.
    provider : Literal['nasdaq']
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
| code | str | CFTC Code of the report. |
| name | str | Name of the underlying asset. |
| category | str | Category of the underlying asset. |
| subcategory | str | Subcategory of the underlying asset. |
| units | str | The units for one contract. |
| symbol | str | Symbol representing the entity requested in the data. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| code | str | CFTC Code of the report. |
| name | str | Name of the underlying asset. |
| category | str | Category of the underlying asset. |
| subcategory | str | Subcategory of the underlying asset. |
| units | str | The units for one contract. |
| symbol | str | Symbol representing the entity requested in the data. |
</TabItem>

</Tabs>

