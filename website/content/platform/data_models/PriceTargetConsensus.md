---
title: Price Target Consensus
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
| `PriceTargetConsensus` | `PriceTargetConsensusQueryParams` | `PriceTargetConsensusData` |

### Import Statement

```python
from openbb_core.provider.standard_models.price_target_consensus import (
PriceTargetConsensusData,
PriceTargetConsensusQueryParams,
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
| symbol | str | Symbol representing the entity requested in the data. |
| target_high | float | High target of the price target consensus. |
| target_low | float | Low target of the price target consensus. |
| target_consensus | float | Consensus target of the price target consensus. |
| target_median | float | Median target of the price target consensus. |
</TabItem>

</Tabs>
