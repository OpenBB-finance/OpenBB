---
title: cik_map
description: Learn how to retrieve the CIK number corresponding to a ticker symbol
  using the python obb.regulators.sec.cik_map function. Understand the available parameters,
  return values, and data structure.
keywords:
- CIK number
- ticker symbol
- python obb.regulators.sec.cik_map function
- get data for symbol
- provider parameter
- returns
- results
- warnings
- chart object
- metadata info
- data
- central index key
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the CIK number corresponding to a ticker symbol.

```python wordwrap
obb.regulators.sec.cik_map(symbol: Union[str, List[str]], provider: Literal[str] = sec)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[CikMap]
        Serializable results.

    provider : Optional[Literal['sec']]
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
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| cik | Union[str, int] | Central Index Key |
</TabItem>

</Tabs>

