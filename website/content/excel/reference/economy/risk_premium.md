<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Market Risk Premium.

```excel wordwrap
=OBB.ECONOMY.RISK_PREMIUM(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp | true |

## Data

| Name | Description |
| ---- | ----------- |
| country | Market country.  |
| continent | Continent of the country.  |
| total_equity_risk_premium | Total equity risk premium for the country.  |
| country_risk_premium | Country-specific risk premium.  |
