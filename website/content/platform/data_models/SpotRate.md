---
title: "Spot Rate"
description: "Spot Rates"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `SpotRate` | `SpotRateQueryParams` | `SpotRateData` |

### Import Statement

```python
from openbb_core.provider.standard_models.spot import (
SpotRateData,
SpotRateQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Union[Union[float, str], List[Union[float, str]]] | Maturities in years. Multiple items allowed for provider(s): fred. | 10.0 | True |
| category | Union[str, List[str]] | Rate category. Options: spot_rate, par_yield. Multiple items allowed for provider(s): fred. | spot_rate | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| maturity | Union[Union[float, str], List[Union[float, str]]] | Maturities in years. Multiple items allowed for provider(s): fred. | 10.0 | True |
| category | Union[str, List[str]] | Rate category. Options: spot_rate, par_yield. Multiple items allowed for provider(s): fred. | spot_rate | True |
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
| rate | float | Spot Rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | Spot Rate. |
</TabItem>

</Tabs>

