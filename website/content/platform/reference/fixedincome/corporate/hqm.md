---
title: "hqm"
description: "Learn about the HQM yield curve and the high quality corporate bond market.  Get information on AAA, AA, and A bonds, market-weighted average quality, corporate  bond rates, maturity, yield curve type, provider, and data."
keywords:
- HQM yield curve
- high quality corporate bond market
- AAA bonds
- AA bonds
- A bonds
- market-weighted average quality
- corporate bond rates
- maturity
- yield curve type
- provider
- fred
- data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/corporate/hqm - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

High Quality Market Corporate Bond.

The HQM yield curve represents the high quality corporate bond market, i.e.,
corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms.
These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve
that is the market-weighted average (MWA) quality of high quality bonds.


Examples
--------

```python
from openbb import obb
obb.fixedincome.corporate.hqm(provider='fred')
obb.fixedincome.corporate.hqm(yield_curve='par', provider='fred')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. | None | True |
| yield_curve | Literal['spot', 'par'] | The yield curve type. | spot | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. | None | True |
| yield_curve | Literal['spot', 'par'] | The yield curve type. | spot | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : HighQualityMarketCorporateBond
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
| rate | float | HighQualityMarketCorporateBond Rate. |
| maturity | str | Maturity. |
| yield_curve | Literal['spot', 'par'] | The yield curve type. |
</TabItem>

<TabItem value='fred' label='fred'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| date | date | The date of the data. |
| rate | float | HighQualityMarketCorporateBond Rate. |
| maturity | str | Maturity. |
| yield_curve | Literal['spot', 'par'] | The yield curve type. |
| series_id | str | FRED series id. |
</TabItem>

</Tabs>

