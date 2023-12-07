---
title: Futures Historical Price
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
| `FuturesCurve` | `FuturesCurveQueryParams` | `FuturesCurveData` |

### Import Statement

```python
from openbb_core.provider.standard_models.futures_curve import (
FuturesCurveData,
FuturesCurveQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| date | date | A specific date to get data for. | None | True |
| provider | Literal['cboe', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| expiration | str | Futures expiration month. |
| price | float | The close price. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| expiration | str | Futures expiration month. |
| price | float | The close price. |
| symbol | str | The trading symbol for the tenor of future. |
</TabItem>

</Tabs>
