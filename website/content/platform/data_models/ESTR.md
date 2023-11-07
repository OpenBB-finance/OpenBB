---
title: Euro Short-Term Rate
description: Instructions on how to use the ESTR Query Parameters and Data Classes
  in Python. Includes information on importing the classes, setting parameters and
  interpreting the data.
keywords:
- ESTR
- query parameters
- data class
- Python
- import statement
- start date
- end date
- provider
- fred
- data interpretation
- volume weighted trimmed mean rate
- number of transactions
- number of active banks
- total volume
- share of volume of the 5 largest active banks
- rate at 75th percentile of volume
- rate at 25th percentile of volume
- rate
- date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Euro Short-Term Rate - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `ESTR` | `ESTRQueryParams` | `ESTRData` |

### Import Statement

```python
from openbb_provider.standard_models.estr_rates import (
ESTRData,
ESTRQueryParams,
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
| parameter | Literal['volume_weighted_trimmed_mean_rate', 'number_of_transactions', 'number_of_active_banks', 'total_volume', 'share_of_volume_of_the_5_largest_active_banks', 'rate_at_75th_percentile_of_volume', 'rate_at_25th_percentile_of_volume'] | Period of ESTR rate. | volume_weighted_trimmed_mean_rate | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | ESTR rate. |
</TabItem>

</Tabs>
