---
title: "sectors"
description: "Index Sectors"
keywords:
- index
- sectors
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="index/sectors - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Index Sectors. Sector weighting of an index.


Examples
--------

```python
from openbb import obb
obb.index.sectors(symbol='^TX60', provider='tmx')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| provider | Literal['tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
| use_cache | bool | Whether to use a cached request. All Index data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 1 day. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : IndexSectors
        Serializable results.
    provider : Literal['tmx']
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
| sector | str | The sector name. |
| weight | float | The weight of the sector in the index. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| sector | str | The sector name. |
| weight | float | The weight of the sector in the index. |
</TabItem>

</Tabs>

