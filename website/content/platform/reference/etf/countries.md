---
title: "countries"
description: "Learn about ETF country weighting and how to retrieve country exposure  data using obb.etf.countries API endpoint."
keywords:
- ETF country weighting
- obb.etf.countries
- symbol
- provider
- etf
- data
- results
- chart
- metadata
- country exposure
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/countries - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

ETF Country weighting.


Examples
--------

```python
from openbb import obb
obb.etf.countries(symbol='VT', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, tmx. |  | False |
| provider | Literal['fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, tmx. |  | False |
| provider | Literal['fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. (ETF) Multiple items allowed for provider(s): fmp, tmx. |  | False |
| provider | Literal['fmp', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| use_cache | bool | Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EtfCountries
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
| country | str | The country of the exposure. Corresponding values are normalized percentage points. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| country | str | The country of the exposure. Corresponding values are normalized percentage points. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| country | str | The country of the exposure. Corresponding values are normalized percentage points. |
</TabItem>

</Tabs>

