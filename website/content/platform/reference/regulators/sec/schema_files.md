---
title: "schema_files"
description: "Get lists of SEC XML schema files by year with the OBBect function. Returns  serializable results, provider name, warnings list, chart object, metadata info,  and data including a list of URLs to SEC Schema Files."
keywords:
- SEC XML schema files
- SEC XML schema files by year
- get SEC XML schema files
- OBBect
- Serializable results
- provider name
- warnings list
- chart object
- metadata info
- fetch URL path
- data
- list of URLs to SEC Schema Files
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="regulators/sec/schema_files - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

A tool for navigating the directory of SEC XML schema files by year.


Examples
--------

```python
from openbb import obb
obb.regulators.sec.schema_files(provider='sec')
# Get a list of schema files.
data = obb.regulators.sec.schema_files().results
data.files[0]
'https://xbrl.fasb.org/us-gaap/'
# The directory structure can be navigated by constructing a URL from the 'results' list.
url = data.files[0]+data.files[-1]
# The URL base will always be the 0 position in the list, feed  the URL back in as a parameter.
obb.regulators.sec.schema_files(url=url).results.files
['https://xbrl.fasb.org/us-gaap/2024/'
'USGAAP2024FileList.xml'
'dis/'
'dqcrules/'
'ebp/'
'elts/'
'entire/'
'meta/'
'stm/'
'us-gaap-2024.zip']
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
| url | str | Enter an optional URL path to fetch the next level. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : SchemaFiles
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
| files | List[str] | Dictionary of URLs to SEC Schema Files |
</TabItem>

</Tabs>

