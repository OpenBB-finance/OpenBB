---
title: The RSS feed provides links to litigation releases concerning civil lawsuits brought
    by the Commission in federal court
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `RssLitigation` | `RssLitigationQueryParams` | `RssLitigationData` |

### Import Statement

```python
from openbb_core.provider.standard_models. import (
RssLitigationData,
RssLitigationQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

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
