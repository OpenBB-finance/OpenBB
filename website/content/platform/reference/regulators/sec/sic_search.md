---
title: "sic_search"
description: "Learn how to perform a search for industry titles, reporting office,  and SIC codes using Python. Explore the parameters, returns, and data associated  with the `obb.regulators.sec.sic_search` function."
keywords:
- search
- industry titles
- reporting office
- SIC codes
- Python
- search query
- provider
- cache
- results
- warnings
- chart
- metadata
- data
- sector industrial code
- industry title
- reporting office
- Corporate Finance Office
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="regulators/sec/sic_search - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Search for Industry Titles, Reporting Office, and SIC Codes. An empty query string returns all results.


Examples
--------

```python
from openbb import obb
obb.regulators.sec.sic_search(provider='sec')
obb.regulators.sec.sic_search(query='real estate investment trusts', provider='sec')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| use_cache | bool | Whether or not to use cache. If True, cache will store for seven days. | True | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| use_cache | bool | Whether or not to use cache. If True, cache will store for seven days. | True | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : SicSearch
        Serializable results.
    provider : Literal['sec']
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

</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| sic | int | Sector Industrial Code (SIC) |
| industry | str | Industry title. |
| office | str | Reporting office within the Corporate Finance Office |
</TabItem>

</Tabs>

