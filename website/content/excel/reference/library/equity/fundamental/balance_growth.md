---
title: balance_growth
description: Learn about balance sheet statement growth, equity data for a company,
  parameters like symbol, limit, and provider, and explore the returned results, warnings,
  charts, and metadata. Retrieve detailed data on various balance sheet growth metrics
  like cash and cash equivalents, short-term investments, inventory, total assets,
  total liabilities, and more.
keywords: 
- balance sheet statement growth
- company balance sheet growth
- equity data
- symbol
- limit parameter
- provider parameter
- results
- balance sheet growth
- warnings
- chart
- metadata
- data
- cash and cash equivalents
- short-term investments
- net receivables
- inventory
- current assets
- property, plant, and equipment
- goodwill
- intangible assets
- long-term investments
- tax assets
- other non-current assets
- total non-current assets
- other assets
- total assets
- accounts payable
- short-term debt
- total current liabilities
- long-term debt
- non-current deferred revenue
- non-current deferred tax liabilities
- total non-current liabilities
- common stock
- retained earnings
- accumulated other comprehensive income/loss
- total stockholders' equity
- total liabilities and stockholders' equity
- total investments
- total debt
- net debt
---

<!-- markdownlint-disable MD041 -->

Balance Sheet Statement Growth. Information about the growth of the company balance sheet.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.BALANCE_GROWTH(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |
| limit | Number | The number of data entries to return. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| date | The date of the data.  |
| period | Reporting period.  |
| growth_cash_and_cash_equivalents | Growth rate of cash and cash equivalents.  |
| growth_short_term_investments | Growth rate of short-term investments.  |
| growth_cash_and_short_term_investments | Growth rate of cash and short-term investments.  |
| growth_net_receivables | Growth rate of net receivables.  |
| growth_inventory | Growth rate of inventory.  |
| growth_other_current_assets | Growth rate of other current assets.  |
| growth_total_current_assets | Growth rate of total current assets.  |
| growth_property_plant_equipment_net | Growth rate of net property, plant, and equipment.  |
| growth_goodwill | Growth rate of goodwill.  |
| growth_intangible_assets | Growth rate of intangible assets.  |
| growth_goodwill_and_intangible_assets | Growth rate of goodwill and intangible assets.  |
| growth_long_term_investments | Growth rate of long-term investments.  |
| growth_tax_assets | Growth rate of tax assets.  |
| growth_other_non_current_assets | Growth rate of other non-current assets.  |
| growth_total_non_current_assets | Growth rate of total non-current assets.  |
| growth_other_assets | Growth rate of other assets.  |
| growth_total_assets | Growth rate of total assets.  |
| growth_account_payables | Growth rate of accounts payable.  |
| growth_short_term_debt | Growth rate of short-term debt.  |
| growth_tax_payables | Growth rate of tax payables.  |
| growth_deferred_revenue | Growth rate of deferred revenue.  |
| growth_other_current_liabilities | Growth rate of other current liabilities.  |
| growth_total_current_liabilities | Growth rate of total current liabilities.  |
| growth_long_term_debt | Growth rate of long-term debt.  |
| growth_deferred_revenue_non_current | Growth rate of non-current deferred revenue.  |
| growth_deferrred_tax_liabilities_non_current | Growth rate of non-current deferred tax liabilities.  |
| growth_other_non_current_liabilities | Growth rate of other non-current liabilities.  |
| growth_total_non_current_liabilities | Growth rate of total non-current liabilities.  |
| growth_other_liabilities | Growth rate of other liabilities.  |
| growth_total_liabilities | Growth rate of total liabilities.  |
| growth_common_stock | Growth rate of common stock.  |
| growth_retained_earnings | Growth rate of retained earnings.  |
| growth_accumulated_other_comprehensive_income_loss | Growth rate of accumulated other comprehensive income/loss.  |
| growth_othertotal_stockholders_equity | Growth rate of other total stockholders' equity.  |
| growth_total_stockholders_equity | Growth rate of total stockholders' equity.  |
| growth_total_liabilities_and_stockholders_equity | Growth rate of total liabilities and stockholders' equity.  |
| growth_total_investments | Growth rate of total investments.  |
| growth_total_debt | Growth rate of total debt.  |
| growth_net_debt | Growth rate of net debt.  |
