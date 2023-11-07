---
title: Interest on Reserve Balances
description: This page provides detailed information about implementation and parameters
  of IORB classes including IORB, IORBQueryParams, and IORBData and the way to import
  them using Python. It also explains different parameters like start_date, end_date,
  provider, and how to use them.
keywords:
- IORB
- IORBQueryParams
- IORBData
- Python
- Start_date
- End_date
- Provider
- fred
- Data
- Rate
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Interest on Reserve Balances - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `IORB` | `IORBQueryParams` | `IORBData` |

### Import Statement

```python
from openbb_provider.standard_models.iorb_rates import (
IORBData,
IORBQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | IORB rate. |
</TabItem>

</Tabs>
