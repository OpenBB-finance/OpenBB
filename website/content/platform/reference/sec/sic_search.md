---
title: sic_search
description: Learn how to perform a fuzzy search for industry titles, reporting office,
  and SIC codes using Python. Explore the parameters, returns, and data associated
  with the `obb.regulators.sec.sic_search` function.
keywords:
- fuzzy search
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Fuzzy search for Industry Titles, Reporting Office, and SIC Codes.

```python wordwrap
obb.regulators.sec.sic_search(query: str, provider: Literal[str] = sec)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
| use_cache | bool | Whether to use the cache or not. The full list will be cached for seven days if True. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[SicSearch]
        Serializable results.

    provider : Optional[Literal['sec']]
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
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| sic | int | Sector Industrial Code (SIC) |
| industry | str | Industry title. |
| office | str | Reporting office within the Corporate Finance Office |
</TabItem>

</Tabs>

