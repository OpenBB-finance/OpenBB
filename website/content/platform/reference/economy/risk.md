---
title: risk
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# risk

Market Risk Premium.

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
| total_equity_risk_premium | PositiveFloat | Total equity risk premium for the country. |
| country_risk_premium | NonNegativeFloat | Country-specific risk premium. |
</TabItem>

</Tabs>

