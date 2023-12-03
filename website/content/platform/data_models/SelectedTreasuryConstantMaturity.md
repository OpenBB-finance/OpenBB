---
title: Select Treasury Constant Maturity
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
| `SelectedTreasuryConstantMaturity` | `SelectedTreasuryConstantMaturityQueryParams` | `SelectedTreasuryConstantMaturityData` |

### Import Statement

```python
from openbb_core.provider.standard_models.ffrmc import (
SelectedTreasuryConstantMaturityData,
SelectedTreasuryConstantMaturityQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Literal['10y', '5y', '1y', '6m', '3m'] | The maturity | 10y | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | Selected Treasury Constant Maturity Rate. |
</TabItem>

</Tabs>
