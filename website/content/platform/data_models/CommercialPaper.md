---
title: Commercial Paper
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
| `CommercialPaper` | `CommercialPaperQueryParams` | `CommercialPaperData` |

### Import Statement

```python
from openbb_core.provider.standard_models.cp import (
CommercialPaperData,
CommercialPaperQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Literal['overnight', '7d', '15d', '30d', '60d', '90d'] | The maturity. | 30d | True |
| category | Literal['asset_backed', 'financial', 'nonfinancial'] | The category. | financial | True |
| grade | Literal['aa', 'a2_p2'] | The grade. | aa | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | Commercial Paper Rate. |
</TabItem>

</Tabs>
