---
title: institutional
description: Learn about institutional ownership data, and how to use the OBB.equity.ownership.institutional
  function in Python to access the data. Explore the symbol, include_current_quarter,
  date, and provider parameters. Understand the meaning and usage of the results,
  provider, warnings, chart, and metadata properties. Additionally, get detailed descriptions
  of the various data fields such as symbol, cik, date, investors_holding, number_of_13f_shares,
  total_invested, ownership_percent, new_positions, closed_positions, total_calls,
  total_puts, and put_call_ratio.
keywords: 
- institutional ownership data
- python OBB.equity.ownership.institutional function
- symbol parameter
- include_current_quarter parameter
- date parameter
- provider parameter
- results property
- provider property
- warnings property
- chart property
- metadata property
- data description
- symbol data
- cik data
- date data
- investors_holding data
- last_investors_holding data
- investors_holding_change data
- number_of_13f_shares data
- last_number_of_13f_shares data
- number_of_13f_shares_change data
- total_invested data
- last_total_invested data
- total_invested_change data
- ownership_percent data
- last_ownership_percent data
- ownership_percent_change data
- new_positions data
- last_new_positions data
- new_positions_change data
- increased_positions data
- last_increased_positions data
- increased_positions_change data
- closed_positions data
- last_closed_positions data
- closed_positions_change data
- reduced_positions data
- last_reduced_positions data
- reduced_positions_change data
- total_calls data
- last_total_calls data
- total_calls_change data
- total_puts data
- last_total_puts data
- total_puts_change data
- put_call_ratio data
- last_put_call_ratio data
- put_call_ratio_change data
---

<!-- markdownlint-disable MD041 -->

Institutional Ownership. Institutional ownership data.

## Syntax

```excel wordwrap
=OBB.EQUITY.OWNERSHIP.INSTITUTIONAL(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp, intrinio | True |
| include_current_quarter | Boolean | Include current quarter data. (provider: fmp) | True |
| date | Text | A specific date to get data for. (provider: fmp) | True |
| page_size | Number | The number of data entries to return. (provider: intrinio) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| date | The date of the data.  |
| investors_holding | Number of investors holding the stock. (provider: fmp) |
| last_investors_holding | Number of investors holding the stock in the last quarter. (provider: fmp) |
| investors_holding_change | Change in the number of investors holding the stock. (provider: fmp) |
| number_of_13f_shares | Number of 13F shares. (provider: fmp) |
| last_number_of_13f_shares | Number of 13F shares in the last quarter. (provider: fmp) |
| number_of_13f_shares_change | Change in the number of 13F shares. (provider: fmp) |
| total_invested | Total amount invested. (provider: fmp) |
| last_total_invested | Total amount invested in the last quarter. (provider: fmp) |
| total_invested_change | Change in the total amount invested. (provider: fmp) |
| ownership_percent | Ownership percent. (provider: fmp) |
| last_ownership_percent | Ownership percent in the last quarter. (provider: fmp) |
| ownership_percent_change | Change in the ownership percent. (provider: fmp) |
| new_positions | Number of new positions. (provider: fmp) |
| last_new_positions | Number of new positions in the last quarter. (provider: fmp) |
| new_positions_change | Change in the number of new positions. (provider: fmp) |
| increased_positions | Number of increased positions. (provider: fmp) |
| last_increased_positions | Number of increased positions in the last quarter. (provider: fmp) |
| increased_positions_change | Change in the number of increased positions. (provider: fmp) |
| closed_positions | Number of closed positions. (provider: fmp) |
| last_closed_positions | Number of closed positions in the last quarter. (provider: fmp) |
| closed_positions_change | Change in the number of closed positions. (provider: fmp) |
| reduced_positions | Number of reduced positions. (provider: fmp) |
| last_reduced_positions | Number of reduced positions in the last quarter. (provider: fmp) |
| reduced_positions_change | Change in the number of reduced positions. (provider: fmp) |
| total_calls | Total number of call options contracts traded for Apple Inc. on the specified date. (provider: fmp) |
| last_total_calls | Total number of call options contracts traded for Apple Inc. on the previous reporting date. (provider: fmp) |
| total_calls_change | Change in the total number of call options contracts traded between the current and previous reporting dates. (provider: fmp) |
| total_puts | Total number of put options contracts traded for Apple Inc. on the specified date. (provider: fmp) |
| last_total_puts | Total number of put options contracts traded for Apple Inc. on the previous reporting date. (provider: fmp) |
| total_puts_change | Change in the total number of put options contracts traded between the current and previous reporting dates. (provider: fmp) |
| put_call_ratio | Put-call ratio, which is the ratio of the total number of put options to call options traded on the specified date. (provider: fmp) |
| last_put_call_ratio | Put-call ratio on the previous reporting date. (provider: fmp) |
| put_call_ratio_change | Change in the put-call ratio between the current and previous reporting dates. (provider: fmp) |
| name | Name of the institutional owner. (provider: intrinio) |
| value | Value of the institutional owner. (provider: intrinio) |
| amount | Amount of the institutional owner. (provider: intrinio) |
| sole_voting_authority | Sole voting authority of the institutional owner. (provider: intrinio) |
| shared_voting_authority | Shared voting authority of the institutional owner. (provider: intrinio) |
| no_voting_authority | No voting authority of the institutional owner. (provider: intrinio) |
| previous_amount | Previous amount of the institutional owner. (provider: intrinio) |
| amount_change | Amount change of the institutional owner. (provider: intrinio) |
| amount_percent_change | Amount percent change of the institutional owner. (provider: intrinio) |
