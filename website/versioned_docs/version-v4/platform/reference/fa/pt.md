---
title: pt
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pt

Price Target Consensus.

```python wordwrap
pt(symbol: Union[str, List[str]], provider: Union[Literal[str]] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[PriceTargetConsensus]
        Serializable results.

    provider : Optional[Literal[Union[Literal['fmp'], NoneType]]
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
| target_high | Union[float] | High target of the price target consensus. |
| target_low | Union[float] | Low target of the price target consensus. |
| target_consensus | Union[float] | Consensus target of the price target consensus. |
| target_median | Union[float] | Median target of the price target consensus. |
</TabItem>

</Tabs>

