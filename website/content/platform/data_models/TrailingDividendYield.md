---
title: TrailingDividendYield
description: Trailing 1yr dividend yield
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `TrailingDividendYield` | `TrailingDividendYieldQueryParams` | `TrailingDividendYieldData` |

### Import Statement

```python
from openbb_provider.standard_models. import (
TrailingDividendYieldData,
TrailingDividendYieldQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['tiingo'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tiingo' if there is no default. | tiingo | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| trailing_dividend_yield | float | Trailing dividend yield. |
</TabItem>

</Tabs>

