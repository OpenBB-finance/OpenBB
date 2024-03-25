---
title: "Latest Attributes"
description: "Get the latest value of a data tag from Intrinio"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `LatestAttributes` | `LatestAttributesQueryParams` | `LatestAttributesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.latest_attributes import (
LatestAttributesData,
LatestAttributesQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): intrinio. |  | False |
| tag | Union[str, List[str]] | Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio. |  | False |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): intrinio. |  | False |
| tag | Union[str, List[str]] | Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio. |  | False |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| tag | str | Tag name for the fetched data. |
| value | Union[str, float] | The value of the data. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| tag | str | Tag name for the fetched data. |
| value | Union[str, float] | The value of the data. |
</TabItem>

</Tabs>

