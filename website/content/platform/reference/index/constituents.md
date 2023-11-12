---
title: constituents
description: Learn how to fetch constituents of an index using the OBB library in
  Python. Get detailed information such as symbol, name, sector, sub-sector, headquarters,
  date of first addition, CIK, and founding year of the constituent companies in the
  index.
keywords:
- index constituents
- fetch constituents
- index constituents parameters
- index constituents returns
- index constituents data
- index constituents symbol
- index constituents name
- index constituents sector
- index constituents sub-sector
- index constituents headquarters
- index constituents date first added
- index constituents cik
- index constituents founding year
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Index Constituents. Constituents of an index.

```python wordwrap
obb.index.constituents(index: Literal[str] = dowjones, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| index | Literal['nasdaq', 'sp500', 'dowjones'] | Index for which we want to fetch the constituents. | dowjones | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[IndexConstituents]
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
| name | str | Name of the constituent company in the index. |
| sector | str | Sector the constituent company in the index belongs to. |
| sub_sector | str | Sub-sector the constituent company in the index belongs to. |
| headquarter | str | Location of the headquarter of the constituent company in the index. |
| date_first_added | Union[str, date] | Date the constituent company was added to the index. |
| cik | int | Central Index Key of the constituent company in the index. |
| founded | Union[str, date] | Founding year of the constituent company in the index. |
</TabItem>

</Tabs>

