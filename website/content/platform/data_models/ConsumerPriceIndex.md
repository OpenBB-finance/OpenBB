---
title: "Consumer Price Index"
description: "Consumer Price Index (CPI)"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `ConsumerPriceIndex` | `ConsumerPriceIndexQueryParams` | `ConsumerPriceIndexData` |

### Import Statement

```python
from openbb_core.provider.standard_models.cpi import (
ConsumerPriceIndexData,
ConsumerPriceIndexQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | Union[str, List[str]] | The country to get data. Multiple items allowed for provider(s): fred. |  | False |
| units | Literal['growth_previous', 'growth_same', 'index_2015'] | The unit of measurement for the data.   Options:   - `growth_previous`: Percent growth from the previous period.    If monthly data, this is month-over-month, etc   - `growth_same`: Percent growth from the same period in the previous year.    If looking at monthly data, this would be year-over-year, etc.   - `index_2015`: Rescaled index value, such that the value in 2015 is 100. | growth_same | True |
| frequency | Literal['monthly', 'quarter', 'annual'] | The frequency of the data.   Options: `monthly`, `quarter`, and `annual`. | monthly | True |
| harmonized | bool | Whether you wish to obtain harmonized data. | False | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | Union[str, List[str]] | The country to get data. Multiple items allowed for provider(s): fred. |  | False |
| units | Literal['growth_previous', 'growth_same', 'index_2015'] | The unit of measurement for the data.   Options:   - `growth_previous`: Percent growth from the previous period.    If monthly data, this is month-over-month, etc   - `growth_same`: Percent growth from the same period in the previous year.    If looking at monthly data, this would be year-over-year, etc.   - `index_2015`: Rescaled index value, such that the value in 2015 is 100. | growth_same | True |
| frequency | Literal['monthly', 'quarter', 'annual'] | The frequency of the data.   Options: `monthly`, `quarter`, and `annual`. | monthly | True |
| harmonized | bool | Whether you wish to obtain harmonized data. | False | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
</TabItem>

</Tabs>

