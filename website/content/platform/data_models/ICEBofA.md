---
title: ICE BofA US Corporate Bond Indices
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
| `ICEBofA` | `ICEBofAQueryParams` | `ICEBofAData` |

### Import Statement

```python
from openbb_core.provider.standard_models.ice_bofa import (
ICEBofAData,
ICEBofAQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| index_type | Literal['yield', 'yield_to_worst', 'total_return', 'spread'] | The type of series. | yield | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| index_type | Literal['yield', 'yield_to_worst', 'total_return', 'spread'] | The type of series. | yield | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| category | Literal['all', 'duration', 'eur', 'usd'] | The type of category. | all | True |
| area | Literal['asia', 'emea', 'eu', 'ex_g10', 'latin_america', 'us'] | The type of area. | us | True |
| grade | Literal['a', 'aa', 'aaa', 'b', 'bb', 'bbb', 'ccc', 'crossover', 'high_grade', 'high_yield', 'non_financial', 'non_sovereign', 'private_sector', 'public_sector'] | The type of grade. | non_sovereign | True |
| options | bool | Whether to include options in the results. | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | ICE BofA US Corporate Bond Indices Rate. |
</TabItem>

</Tabs>
