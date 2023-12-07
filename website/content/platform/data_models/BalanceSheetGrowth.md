---
title: Balance Sheet Statement Growth
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
| `BalanceSheetGrowth` | `BalanceSheetGrowthQueryParams` | `BalanceSheetGrowthData` |

### Import Statement

```python
from openbb_core.provider.standard_models.balance_sheet_growth import (
BalanceSheetGrowthData,
BalanceSheetGrowthQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 10 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| date | date | The date of the data. |
| period | str | Reporting period. |
| growth_cash_and_cash_equivalents | float | Growth rate of cash and cash equivalents. |
| growth_short_term_investments | float | Growth rate of short-term investments. |
| growth_cash_and_short_term_investments | float | Growth rate of cash and short-term investments. |
| growth_net_receivables | float | Growth rate of net receivables. |
| growth_inventory | float | Growth rate of inventory. |
| growth_other_current_assets | float | Growth rate of other current assets. |
| growth_total_current_assets | float | Growth rate of total current assets. |
| growth_property_plant_equipment_net | float | Growth rate of net property, plant, and equipment. |
| growth_goodwill | float | Growth rate of goodwill. |
| growth_intangible_assets | float | Growth rate of intangible assets. |
| growth_goodwill_and_intangible_assets | float | Growth rate of goodwill and intangible assets. |
| growth_long_term_investments | float | Growth rate of long-term investments. |
| growth_tax_assets | float | Growth rate of tax assets. |
| growth_other_non_current_assets | float | Growth rate of other non-current assets. |
| growth_total_non_current_assets | float | Growth rate of total non-current assets. |
| growth_other_assets | float | Growth rate of other assets. |
| growth_total_assets | float | Growth rate of total assets. |
| growth_account_payables | float | Growth rate of accounts payable. |
| growth_short_term_debt | float | Growth rate of short-term debt. |
| growth_tax_payables | float | Growth rate of tax payables. |
| growth_deferred_revenue | float | Growth rate of deferred revenue. |
| growth_other_current_liabilities | float | Growth rate of other current liabilities. |
| growth_total_current_liabilities | float | Growth rate of total current liabilities. |
| growth_long_term_debt | float | Growth rate of long-term debt. |
| growth_deferred_revenue_non_current | float | Growth rate of non-current deferred revenue. |
| growth_deferrred_tax_liabilities_non_current | float | Growth rate of non-current deferred tax liabilities. |
| growth_other_non_current_liabilities | float | Growth rate of other non-current liabilities. |
| growth_total_non_current_liabilities | float | Growth rate of total non-current liabilities. |
| growth_other_liabilities | float | Growth rate of other liabilities. |
| growth_total_liabilities | float | Growth rate of total liabilities. |
| growth_common_stock | float | Growth rate of common stock. |
| growth_retained_earnings | float | Growth rate of retained earnings. |
| growth_accumulated_other_comprehensive_income_loss | float | Growth rate of accumulated other comprehensive income/loss. |
| growth_othertotal_stockholders_equity | float | Growth rate of other total stockholders' equity. |
| growth_total_stockholders_equity | float | Growth rate of total stockholders' equity. |
| growth_total_liabilities_and_stockholders_equity | float | Growth rate of total liabilities and stockholders' equity. |
| growth_total_investments | float | Growth rate of total investments. |
| growth_total_debt | float | Growth rate of total debt. |
| growth_net_debt | float | Growth rate of net debt. |
</TabItem>

</Tabs>
