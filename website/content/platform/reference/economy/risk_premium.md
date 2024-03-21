---
title: "risk_premium"
description: "Learn about Historical Market Risk Premium and the obb.economy.risk_premium  function. Explore the parameters, returns, and data available, including results,  warnings, chart, metadata, country, continent, total equity risk premium, and country  risk premium."
keywords:
- Historical Market Risk Premium
- obb.economy.risk_premium
- parameters
- provider
- returns
- OBBject
- results
- RiskPremium
- warnings
- chart
- metadata
- data
- country
- continent
- total equity risk premium
- country risk premium
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy/risk_premium - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Market Risk Premium by country.


Examples
--------

```python
from openbb import obb
obb.economy.risk_premium(provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : RiskPremium
        Serializable results.
    provider : Literal['fmp']
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
| country | str | Market country. |
| continent | str | Continent of the country. |
| total_equity_risk_premium | float, Gt(gt=0) | Total equity risk premium for the country. |
| country_risk_premium | float, Ge(ge=0) | Country-specific risk premium. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| country | str | Market country. |
| continent | str | Continent of the country. |
| total_equity_risk_premium | float, Gt(gt=0) | Total equity risk premium for the country. |
| country_risk_premium | float, Ge(ge=0) | Country-specific risk premium. |
</TabItem>

</Tabs>

