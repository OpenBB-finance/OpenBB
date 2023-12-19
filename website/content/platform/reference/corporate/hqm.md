---
title: hqm
description: Learn about the HQM yield curve and the high quality corporate bond market.
  Get information on AAA, AA, and A bonds, market-weighted average quality, corporate
  bond rates, maturity, yield curve type, provider, and data.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

High Quality Market Corporate Bond.

The HQM yield curve represents the high quality corporate bond market, i.e.,
corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms.
These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve
that is the market-weighted average (MWA) quality of high quality bonds.

```python wordwrap
obb.fixedincome.corporate.hqm(date: date = None, yield_curve: List[Literal[list]] = ['spot'], provider: Literal[str] = fred)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | date | The date of the data. | None | True |
| yield_curve | List[Literal['spot', 'par']] | The yield curve type. | ['spot'] | True |
| provider | Literal['fred'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fred' if there is no default. | fred | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[HighQualityMarketCorporateBond]
        Serializable results.

    provider : Optional[Literal['fred']]
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
| date | date | The date of the data. |
| rate | float | HighQualityMarketCorporateBond Rate. |
| maturity | str | Maturity. |
| yield_curve | Literal['spot', 'par'] | The yield curve type. |
</TabItem>

</Tabs>

