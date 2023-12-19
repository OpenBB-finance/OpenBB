---
title: sectors
description: Learn about ETF sector weighting using OBB.etf.sectors API. Find information
  about the parameters, returns, and data, including sectors, weights, and exposure
  levels in normalized percentage points.
keywords:
- ETF Sector weighting
- OBB.etf.sectors
- parameters
- symbol
- provider
- returns
- results
- etf sectors
- warnings
- chart
- metadata
- data
- sector
- weight
- exposure
- normalized percentage points
---



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

ETF Sector weighting.

```python wordwrap
obb.etf.sectors(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EtfSectors]
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
| sector | str | Sector of exposure. |
| weight | float | Exposure of the ETF to the sector in normalized percentage points. |
</TabItem>

</Tabs>

