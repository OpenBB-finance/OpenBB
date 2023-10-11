---
title: Curated Commitment of Traders Reports
description: OpenBB Platform Data Model
---


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
from openbb_provider.standard_models. import (
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
| provider | Union[Literal['quandl']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'quandl' if there is no default. | quandl | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| code | str | CFTC Code of the report. |
| name | str | Name of the underlying asset. |
| category | Union[str] | Category of the underlying asset. |
| subcategory | Union[str] | Subcategory of the underlying asset. |
| units | Union[str] | The units for one contract. |
| symbol | Union[str] | Trading symbol representing the underlying asset. |
</TabItem>

</Tabs>

