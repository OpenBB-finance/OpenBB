---
title: Market Risk Premium
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `RiskPremium` | `RiskPremiumQueryParams` | `RiskPremiumData` |

### Import Statement

```python
from openbb_provider.standard_models.risk_premium import (
RiskPremiumData,
RiskPremiumQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| country | str | Market country. |
| continent | Union[str] | Continent of the country. |
| total_equity_risk_premium | Union[typing_extensions.Annotated[float, Gt(gt=0)]] | Total equity risk premium for the country. |
| country_risk_premium | Union[typing_extensions.Annotated[float, Ge(ge=0)]] | Country-specific risk premium. |
</TabItem>

</Tabs>

