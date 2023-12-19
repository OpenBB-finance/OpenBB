---
title: Historical Market Risk Premium
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

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
from openbb_core.provider.standard_models.risk_premium import (
RiskPremiumData,
RiskPremiumQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

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
