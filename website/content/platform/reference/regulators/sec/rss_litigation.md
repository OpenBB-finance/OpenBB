---
title: "rss_litigation"
description: "Learn how to use the RSS feed to access litigation releases, including  civil lawsuits brought by the Commission in federal court. This documentation provides  details about the 'obb.regulators.sec.rss_litigation' python function, its parameters  and return values, as well as the data structure used for the releases."
keywords:
- RSS feed
- litigation releases
- civil lawsuits
- Commission
- federal court
- python
- obb.regulators.sec.rss_litigation
- provider
- parameters
- returns
- data
- published
- title
- summary
- id
- link
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="regulators/sec/rss_litigation - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

The RSS feed provides links to litigation releases concerning civil lawsuits brought by the Commission in federal court.


Examples
--------

```python
from openbb import obb
obb.regulators.sec.rss_litigation(provider='sec')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : RssLitigation
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
| published | datetime | The date of publication. |
| title | str | The title of the release. |
| summary | str | Short summary of the release. |
| id | str | The identifier associated with the release. |
| link | str | URL to the release. |
</TabItem>

</Tabs>

