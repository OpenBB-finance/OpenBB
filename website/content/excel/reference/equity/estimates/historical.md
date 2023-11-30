<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Analyst Estimates. Analyst stock recommendations.

```excel wordwrap
=OBB.EQUITY.ESTIMATES.HISTORICAL(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |
| period | string | Time period of the data to return. | true |
| limit | number | The number of data entries to return. | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| estimated_revenue_low | Estimated revenue low.  |
| estimated_revenue_high | Estimated revenue high.  |
| estimated_revenue_avg | Estimated revenue average.  |
| estimated_ebitda_low | Estimated EBITDA low.  |
| estimated_ebitda_high | Estimated EBITDA high.  |
| estimated_ebitda_avg | Estimated EBITDA average.  |
| estimated_ebit_low | Estimated EBIT low.  |
| estimated_ebit_high | Estimated EBIT high.  |
| estimated_ebit_avg | Estimated EBIT average.  |
| estimated_net_income_low | Estimated net income low.  |
| estimated_net_income_high | Estimated net income high.  |
| estimated_net_income_avg | Estimated net income average.  |
| estimated_sga_expense_low | Estimated SGA expense low.  |
| estimated_sga_expense_high | Estimated SGA expense high.  |
| estimated_sga_expense_avg | Estimated SGA expense average.  |
| estimated_eps_avg | Estimated EPS average.  |
| estimated_eps_high | Estimated EPS high.  |
| estimated_eps_low | Estimated EPS low.  |
| number_analyst_estimated_revenue | Number of analysts who estimated revenue.  |
| number_analysts_estimated_eps | Number of analysts who estimated EPS.  |
