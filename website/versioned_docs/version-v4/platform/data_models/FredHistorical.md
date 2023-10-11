---
title: Fred Historical
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `FredHistorical` | `FredHistoricalQueryParams` | `FredHistoricalData` |

### Import Statement

```python
from openbb_provider.standard_models.fred_historical import (
FredHistoricalData,
FredHistoricalQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | Union[int] | The number of data entries to return. | 100 | True |
| provider | Union[Literal['intrinio']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| limit | Union[int] | The number of data entries to return. | 100 | True |
| provider | Union[Literal['intrinio']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
| next_page | Union[str] | Token to get the next page of data from a previous API call. | None | True |
| all_pages | Union[bool] | Returns all pages of data from the API call at once. | False | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| value | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | Value of the index. |
</TabItem>

</Tabs>

