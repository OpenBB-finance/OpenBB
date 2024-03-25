---
title: "Index Sectors"
description: "Index Sectors"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `IndexSectors` | `IndexSectorsQueryParams` | `IndexSectorsData` |

### Import Statement

```python
from openbb_core.provider.standard_models.index_sectors import (
IndexSectorsData,
IndexSectorsQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
| use_cache | bool | Whether to use a cached request. All Index data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 1 day. | True | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| sector | str | The sector name. |
| weight | float | The weight of the sector in the index. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| sector | str | The sector name. |
| weight | float | The weight of the sector in the index. |
</TabItem>

</Tabs>

