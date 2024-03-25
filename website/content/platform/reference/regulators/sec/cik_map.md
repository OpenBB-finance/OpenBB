---
title: "cik_map"
description: "Learn how to retrieve the CIK number corresponding to a ticker symbol  using the python obb.regulators.sec.cik_map function. Understand the available parameters,  return values, and data structure."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="regulators/sec/cik_map - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Map a ticker symbol to a CIK number.


Examples
--------

```python
from openbb import obb
obb.regulators.sec.cik_map(symbol='MSFT', provider='sec')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'sec' if there is no default. | sec | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CikMap
        Serializable results.
    provider : Literal['sec']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| cik | Union[int, str] | Central Index Key (CIK) for the requested entity. |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| cik | Union[int, str] | Central Index Key (CIK) for the requested entity. |
</TabItem>

</Tabs>

