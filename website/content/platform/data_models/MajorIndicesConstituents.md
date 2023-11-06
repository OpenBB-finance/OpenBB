---
title: Major Indices Constituents
description: This documentation page provides details about the implementation of
  MajorIndicesConstituents, including parameters and data classes. It describes how
  to retrieve information about the companies listed on major indices.
keywords:
- implementation
- major indices constituents
- parameters
- data
- index
- standard_models
- sector
- provider
- constituent company
- sub-sector
- headquarter
- date first added
- central index key
- founded
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Major Indices Constituents - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `MajorIndicesConstituents` | `MajorIndicesConstituentsQueryParams` | `MajorIndicesConstituentsData` |

### Import Statement

```python
from openbb_provider.standard_models.major_indices_constituents import (
MajorIndicesConstituentsData,
MajorIndicesConstituentsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| index | Literal['nasdaq', 'sp500', 'dowjones'] | Index for which we want to fetch the constituents. | dowjones | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| name | str | Name of the constituent company in the index. |
| sector | str | Sector the constituent company in the index belongs to. |
| sub_sector | str | Sub-sector the constituent company in the index belongs to. |
| headquarter | str | Location of the headquarter of the constituent company in the index. |
| date_first_added | Union[date, str] | Date the constituent company was added to the index. |
| cik | int | Central Index Key of the constituent company in the index. |
| founded | Union[date, str] | Founding year of the constituent company in the index. |
</TabItem>

</Tabs>
