---
title: pt
description: This page provides insights on how to query and retrieve 'Price Target
  Consensus' data for selected symbols using a specified provider. It includes explanations
  for the parameters needed, the data returned, and how to handle specific sequences
  of commands.
keywords:
- Price Target Consensus
- Data Provider
- FMP
- Symbol Data
- Price Target
- Consensus Target
- High Target
- Low Target
- Median Target
- Chart Object
- Command Execution
- Python Wordwrap
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="pt - Fa - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pt

Price Target Consensus. Price target consensus data.

```python wordwrap
pt(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[PriceTargetConsensus]
        Serializable results.

    provider : Optional[Literal['fmp']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

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
