---
title: "Search Attributes"
description: "Search Intrinio data tags to search in latest or historical attributes"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `SearchAttributes` | `SearchAttributesQueryParams` | `SearchAttributesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.search_attributes import (
SearchAttributesData,
SearchAttributesQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Query to search for. |  | False |
| limit | int | The number of data entries to return. | 1000 | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Query to search for. |  | False |
| limit | int | The number of data entries to return. | 1000 | True |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| id | str | ID of the financial attribute. |
| name | str | Name of the financial attribute. |
| tag | str | Tag of the financial attribute. |
| statement_code | str | Code of the financial statement. |
| statement_type | str | Type of the financial statement. |
| parent_name | str | Parent's name of the financial attribute. |
| sequence | int | Sequence of the financial statement. |
| factor | str | Unit of the financial attribute. |
| transaction | str | Transaction type (credit/debit) of the financial attribute. |
| type | str | Type of the financial attribute. |
| unit | str | Unit of the financial attribute. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| id | str | ID of the financial attribute. |
| name | str | Name of the financial attribute. |
| tag | str | Tag of the financial attribute. |
| statement_code | str | Code of the financial statement. |
| statement_type | str | Type of the financial statement. |
| parent_name | str | Parent's name of the financial attribute. |
| sequence | int | Sequence of the financial statement. |
| factor | str | Unit of the financial attribute. |
| transaction | str | Transaction type (credit/debit) of the financial attribute. |
| type | str | Type of the financial attribute. |
| unit | str | Unit of the financial attribute. |
</TabItem>

</Tabs>

