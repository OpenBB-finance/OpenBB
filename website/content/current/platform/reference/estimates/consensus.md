---
title: consensus
description: Learn how to access and use the Price Target Consensus functionality
  in your application. Explore the available parameters and understand the returned
  data structure.
keywords:
- Price target consensus data
- equity estimates consensus
- symbol parameter
- provider parameter
- results attribute
- provider attribute
- warnings attribute
- chart attribute
- metadata attribute
- data table
- target_high column
- target_low column
- target_consensus column
- target_median column
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Price Target Consensus. Price target consensus data.

```python wordwrap
obb.equity.estimates.consensus(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
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
| symbol | str | Symbol representing the entity requested in the data. |
| target_high | float | High target of the price target consensus. |
| target_low | float | Low target of the price target consensus. |
| target_consensus | float | Consensus target of the price target consensus. |
| target_median | float | Median target of the price target consensus. |
</TabItem>

</Tabs>

