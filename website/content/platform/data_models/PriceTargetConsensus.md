---
title: Price Target Consensus
description: OpenBB Platform Data Model
---


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
from openbb_provider.standard_models.price_target_consensus import (
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
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| target_high | Union[float] | High target of the price target consensus. |
| target_low | Union[float] | Low target of the price target consensus. |
| target_consensus | Union[float] | Consensus target of the price target consensus. |
| target_median | Union[float] | Median target of the price target consensus. |
</TabItem>

</Tabs>

