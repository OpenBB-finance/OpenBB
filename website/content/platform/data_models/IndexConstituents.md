---
title: Index Constituents
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
| `IndexConstituents` | `IndexConstituentsQueryParams` | `IndexConstituentsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.index_constituents import (
IndexConstituentsData,
IndexConstituentsQueryParams,
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
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the constituent company in the index. |
| sector | str | Sector the constituent company in the index belongs to. |
| sub_sector | str | Sub-sector the constituent company in the index belongs to. |
| headquarter | str | Location of the headquarter of the constituent company in the index. |
| date_first_added | Union[str, date] | Date the constituent company was added to the index. |
| cik | int | Central Index Key of the constituent company in the index. |
| founded | Union[str, date] | Founding year of the constituent company in the index. |
</TabItem>

</Tabs>
