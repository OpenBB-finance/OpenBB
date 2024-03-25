---
title: "latest_attributes"
description: "Get the latest value of a data tag from Intrinio"
keywords:
- equity
- fundamental
- latest_attributes
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/latest_attributes - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the latest value of a data tag from Intrinio.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.latest_attributes(symbol='AAPL', tag='ceo', provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): intrinio. |  | False |
| tag | Union[str, List[str]] | Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio. |  | False |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): intrinio. |  | False |
| tag | Union[str, List[str]] | Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio. |  | False |
| provider | Literal['intrinio'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'intrinio' if there is no default. | intrinio | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : LatestAttributes
        Serializable results.
    provider : Literal['intrinio']
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
| symbol | str | Symbol representing the entity requested in the data. |
| tag | str | Tag name for the fetched data. |
| value | Union[str, float] | The value of the data. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| tag | str | Tag name for the fetched data. |
| value | Union[str, float] | The value of the data. |
</TabItem>

</Tabs>

