---
title: risk
description: This page provides detailed information about the calculation of market
  risk premium including its historical data. It includes parameters for provider
  selection, returns comprising of results, provider name, warning lists, chart object,
  and metadata. Also, it provides a data section explaining the country and continental
  data and their respective risk premiums.
keywords:
- market risk premium
- historical market risk premium
- risk parameters
- provider selection
- warning list
- chart object
- continental data
- country-specific risk premium
- metadata information
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.risk - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# risk

Market Risk Premium. Historical market risk premium.

```python wordwrap
risk(provider: Literal[str] = fmp)
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
