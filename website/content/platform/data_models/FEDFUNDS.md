---
title: "Fedfunds"
description: "Fed Funds Rate"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

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
from openbb_core.provider.standard_models. import (
FEDFUNDSData,
FEDFUNDSQueryParams,
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
| provider | Literal['federal_reserve', 'fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'federal_reserve' if there is no default. | federal_reserve | True |
</TabItem>

<TabItem value='federal_reserve' label='federal_reserve'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['federal_reserve', 'fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'federal_reserve' if there is no default. | federal_reserve | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['federal_reserve', 'fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'federal_reserve' if there is no default. | federal_reserve | True |
| parameter | Literal['monthly', 'daily', 'weekly', 'daily_excl_weekend', 'annual', 'biweekly', 'volume'] | Period of FED rate. | weekly | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | FED rate. |
</TabItem>

<TabItem value='federal_reserve' label='federal_reserve'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | FED rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | FED rate. |
</TabItem>

</Tabs>

