---
title: Fed Funds Rate
description: This page provides detailed information on the implementation, parameters
  and data associated with FEDFUNDS, including FEDFUNDSQueryParams and FEDFUNDSData.
  Learn how to effectively use the FED rate and familiarize yourself with the Python
  Import Statement.
keywords:
- FEDFUNDS
- FEDFUNDSQueryParams
- FEDFUNDSData
- FED rate
- Implementation details
- Python
- Import Statement
- Parameters
- Data
- Class names
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Fed Funds Rate - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `FEDFUNDS` | `FEDFUNDSQueryParams` | `FEDFUNDSData` |

### Import Statement

```python
from openbb_provider.standard_models. import (
FEDFUNDSData,
FEDFUNDSQueryParams,
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

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| parameter | Literal['monthly', 'daily', 'weekly', 'daily_excl_weekend', 'annual', 'biweekly', 'volume'] | Period of FED rate. | weekly | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | FED rate. |
</TabItem>

</Tabs>
