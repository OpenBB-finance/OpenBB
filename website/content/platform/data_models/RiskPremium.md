---
title: Market Risk Premium
description: This page provides technical documentation on the implementation of the
  'RiskPremium' class with parameters and data attributes. It involves understanding
  Python syntax and detailed explanation of each attribute.
keywords:
- Docusaurus
- Metadata
- SEO
- Risk
- Premium
- Implementation
- Python
- Parameters
- Data
- Class names
- Query
- Country
- Continent
- Market
- Equity
- FMP
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Market Risk Premium - Data_Models | OpenBB Platform Docs" />


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
