---
title: Weekly aggregate trade data for Over The Counter deals
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
| `OTCAggregate` | `OTCAggregateQueryParams` | `OTCAggregateData` |

### Import Statement

```python
from openbb_core.provider.standard_models.otc_aggregate import (
OTCAggregateData,
OTCAggregateQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['finra'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finra' if there is no default. | finra | True |
</TabItem>

<TabItem value='finra' label='finra'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. | None | True |
| provider | Literal['finra'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finra' if there is no default. | finra | True |
| tier | Literal['T1', 'T2', 'OTCE'] | "T1 - Securities included in the S&P 500, Russell 1000 and selected exchange-traded products;
        T2 - All other NMS stocks; OTC - Over-the-Counter equity securities | T1 | True |
| is_ats | bool | ATS data if true, NON-ATS otherwise | True | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| update_date | date | Most recent date on which total trades is updated based on data received from each ATS/OTC. |
| share_quantity | float | Aggregate weekly total number of shares reported by each ATS for the Symbol. |
| trade_quantity | float | Aggregate weekly total number of trades reported by each ATS for the Symbol |
</TabItem>

</Tabs>
