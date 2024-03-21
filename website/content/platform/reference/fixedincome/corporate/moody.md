---
title: "moody"
description: "Moody Corporate Bond Index"
keywords:
- fixedincome
- corporate
- moody
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/corporate/moody - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Moody Corporate Bond Index.

Moody's Aaa and Baa are investment bonds that acts as an index of
the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively.
These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year
Treasury Bill as an indicator of the interest rate.


Examples
--------

```python
from openbb import obb
obb.fixedincome.corporate.moody(provider='fred')
obb.fixedincome.corporate.moody(index_type='baa', provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| index_type | Literal['aaa', 'baa'] | The type of series. | aaa | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| index_type | Literal['aaa', 'baa'] | The type of series. | aaa | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
| spread | Literal['treasury', 'fed_funds'] | The type of spread. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : MoodyCorporateBondIndex
        Serializable results.
    provider : Literal['fred']
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
| date | date | The date of the data. |
| rate | float | Moody Corporate Bond Index Rate. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | Moody Corporate Bond Index Rate. |
</TabItem>

</Tabs>

