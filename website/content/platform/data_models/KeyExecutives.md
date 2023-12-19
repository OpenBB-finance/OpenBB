---
title: Key Executives
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
| `KeyExecutives` | `KeyExecutivesQueryParams` | `KeyExecutivesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.key_executives import (
KeyExecutivesData,
KeyExecutivesQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| title | str | Designation of the key executive. |
| name | str | Name of the key executive. |
| pay | int | Pay of the key executive. |
| currency_pay | str | Currency of the pay. |
| gender | str | Gender of the key executive. |
| year_born | int | Birth year of the key executive. |
| title_since | int | Date the tile was held since. |
</TabItem>

</Tabs>
