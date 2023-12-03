---
title: Cryptocurrency Search
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
| `CryptoSearch` | `CryptoSearchQueryParams` | `CryptoSearchData` |

### Import Statement

```python
from openbb_core.provider.standard_models.crypto_search import (
CryptoSearchData,
CryptoSearchQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (Crypto) |
| name | str | Name of the crypto. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (Crypto) |
| name | str | Name of the crypto. |
| currency | str | The currency the crypto trades for. |
| exchange | str | The exchange code the crypto trades on. |
| exchange_name | str | The short name of the exchange the crypto trades on. |
</TabItem>

</Tabs>
