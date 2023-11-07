---
title: Price Target Consensus
description: Documentation for the implementation of PriceTargetConsensus including
  class names, parameters, and data details with their types and descriptions.
keywords:
- Implementation details
- Class names
- Import Statement
- Parameters
- Data
- Tabs
- TabItem
- PriceTargetConsensus
- PriceTargetConsensusQueryParams
- PriceTargetConsensusData
- Symbol
- Provider
- fmp
- Target_high
- Target_low
- Target_consensus
- Target_median
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Price Target Consensus - Data_Models | OpenBB Platform Docs" />


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
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| target_high | float | High target of the price target consensus. |
| target_low | float | Low target of the price target consensus. |
| target_consensus | float | Consensus target of the price target consensus. |
| target_median | float | Median target of the price target consensus. |
</TabItem>

</Tabs>
