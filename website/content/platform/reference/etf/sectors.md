---
title: "sectors"
description: "Learn about ETF sector weighting using OBB.etf.sectors API. Find information  about the parameters, returns, and data, including sectors, weights, and exposure  levels in normalized percentage points."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/sectors - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

ETF Sector weighting.


Examples
--------

```python
from openbb import obb
obb.etf.sectors(symbol='SPY', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| use_cache | bool | Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EtfSectors
        Serializable results.
    provider : Literal['fmp', 'tmx']
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
| sector | str | Sector of exposure. |
| weight | float | Exposure of the ETF to the sector in normalized percentage points. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| sector | str | Sector of exposure. |
| weight | float | Exposure of the ETF to the sector in normalized percentage points. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| sector | str | Sector of exposure. |
| weight | float | Exposure of the ETF to the sector in normalized percentage points. |
</TabItem>

</Tabs>

