---
title: Curated Commitment of Traders Reports
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
| `COTSearch` | `COTSearchQueryParams` | `COTSearchData` |

### Import Statement

```python
from openbb_core.provider.standard_models. import (
COTSearchData,
COTSearchQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['nasdaq'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'nasdaq' if there is no default. | nasdaq | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

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
