---
title: institutions_search
description: Learn how to use the OBB.regulators.sec.institutions_search() method
  to look up institutions regulated by the SEC. This method allows you to search for
  institutions based on various parameters such as the query and provider. It returns
  a list of search results and provides additional attributes like warnings, chart,
  and metadata. Explore the attributes like name and cik for more details on the institution.
keywords:
- institutions regulated by the SEC
- SEC regulated institutions lookup
- SEC regulated institutions search
- SEC institutions search query
- OBB regulator
- InstitutionsSearch class
- provider parameter
- query parameter
- use_cache parameter
- results attribute
- warnings attribute
- chart attribute
- metadata attribute
- name attribute
- cik attribute
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Look up institutions regulated by the SEC.

```python wordwrap
obb.regulators.sec.institutions_search(query: str, provider: Literal[str] = sec)
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
| use_cache | bool | Whether or not to use cache. If True, cache will store for seven days. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[InstitutionsSearch]
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
| name | str | The name of the institution. |
| cik | Union[str, int] | Central Index Key (CIK) |
</TabItem>

</Tabs>

