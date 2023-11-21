---
title: risk_premium
description: Learn about Historical Market Risk Premium and the obb.economy.risk_premium
  function. Explore the parameters, returns, and data available, including results,
  warnings, chart, metadata, country, continent, total equity risk premium, and country
  risk premium.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Market Risk Premium.

```python wordwrap
obb.economy.risk_premium(provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[RiskPremium]
        Serializable results.

    provider : Optional[Literal['fmp']]
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
| country | str | Market country. |
| continent | str | Continent of the country. |
| total_equity_risk_premium | float | Total equity risk premium for the country. |
| country_risk_premium | float | Country-specific risk premium. |
</TabItem>

</Tabs>

