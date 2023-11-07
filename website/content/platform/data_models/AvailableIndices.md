---
title: Available Indices
description: This page provides an in-depth look into the features and details of
  working with AvailableIndices, including parameters and data details. It also provides
  the class names that encapsulate these details and a guide on how to use them in
  your project.
keywords:
- Implementation details
- Class names
- Import Statement
- Parameters
- Data
- AvailableIndices
- AvailableIndicesQueryParams
- AvailableIndicesData
- provider
- fmp
- name
- currency
- stock_exchange
- exchange_short_name
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Available Indices - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `AvailableIndices` | `AvailableIndicesQueryParams` | `AvailableIndicesData` |

### Import Statement

```python
from openbb_provider.standard_models.available_indices import (
AvailableIndicesData,
AvailableIndicesQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the index. |
| currency | str | Currency the index is traded in. |
| stock_exchange | str | Stock exchange where the index is listed. |
| exchange_short_name | str | Short name of the stock exchange where the index is listed. |
</TabItem>

</Tabs>
