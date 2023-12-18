---
title: holdings
description: Learn how to get the holdings data for an individual ETF using the `obb.etf.holdings`
  method. Understand the parameters like symbol, provider, date, and CIK. Explore
  the returns, results, warnings, chart, and metadata. Dive into the data fields like
  symbol, name, LEI, title, CUSIP, ISIN, balance, units, currency, value, weight,
  payoff profile, asset category, issuer category, country, and more.
keywords: 
- ETF holdings
- individual ETF holdings
- holdings data for ETF
- symbol
- provider
- date
- CIK
- returns
- results
- warnings
- chart
- metadata
- data
- name
- LEI
- title
- CUSIP
- ISIN
- balance
- units
- currency
- value
- weight
- payoff profile
- asset category
- issuer category
- country
- is restricted
- fair value level
- is cash collateral
- is non-cash collateral
- is loan by fund
- acceptance datetime
---

<!-- markdownlint-disable MD041 -->

Get the holdings for an individual ETF.

## Syntax

```excel wordwrap
=OBB.ETF.HOLDINGS(required; [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. (ETF) | False |
| provider | Text | Options: fmp | True |
| date | Text | A specific date to get data for. This needs to be _exactly_ the date of the filing. Use the holdings_date command/endpoint to find available filing dates for the ETF. (provider: fmp) | True |
| cik | Text | The CIK of the filing entity. Overrides symbol. (provider: fmp) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data. (ETF)  |
| name | Name of the ETF holding.  |
| lei | The LEI of the holding. (provider: fmp, sec) |
| title | The title of the holding. (provider: fmp) |
| cusip | The CUSIP of the holding. (provider: fmp, sec) |
| isin | The ISIN of the holding. (provider: fmp, sec) |
| balance | The balance of the holding. (provider: fmp, sec) |
| units | The units of the holding. (provider: fmp, sec) |
| currency | The currency of the holding. (provider: fmp, sec) |
| value | The value of the holding in USD. (provider: fmp, sec) |
| weight | The weight of the holding in ETF in %. (provider: fmp, sec) |
| payoff_profile | The payoff profile of the holding. (provider: fmp, sec) |
| asset_category | The asset category of the holding. (provider: fmp, sec) |
| issuer_category | The issuer category of the holding. (provider: fmp, sec) |
| country | The country of the holding. (provider: fmp, sec) |
| is_restricted | Whether the holding is restricted. (provider: fmp, sec) |
| fair_value_level | The fair value level of the holding. (provider: fmp, sec) |
| is_cash_collateral | Whether the holding is cash collateral. (provider: fmp, sec) |
| is_non_cash_collateral | Whether the holding is non-cash collateral. (provider: fmp, sec) |
| is_loan_by_fund | Whether the holding is loan by fund. (provider: fmp, sec) |
| cik | The CIK of the filing. (provider: fmp) |
| acceptance_datetime | The acceptance datetime of the filing. (provider: fmp) |
| other_id | Internal identifier for the holding. (provider: sec) |
| loan_value | The loan value of the holding. (provider: sec) |
| issuer_conditional | The issuer conditions of the holding. (provider: sec) |
| asset_conditional | The asset conditions of the holding. (provider: sec) |
| maturity_date | The maturity date of the debt security. (provider: sec) |
| coupon_kind | The type of coupon for the debt security. (provider: sec) |
| rate_type | The type of rate for the debt security, floating or fixed. (provider: sec) |
| annualized_return | The annualized return on the debt security. (provider: sec) |
| is_default | If the debt security is defaulted. (provider: sec) |
| in_arrears | If the debt security is in arrears. (provider: sec) |
| is_paid_kind | If the debt security payments are are paid in kind. (provider: sec) |
| derivative_category | The derivative category of the holding. (provider: sec) |
| counterparty | The counterparty of the derivative. (provider: sec) |
| underlying_name | The name of the underlying asset associated with the derivative. (provider: sec) |
| option_type | The type of option. (provider: sec) |
| derivative_payoff | The payoff profile of the derivative. (provider: sec) |
| expiry_date | The expiry or termination date of the derivative. (provider: sec) |
| exercise_price | The exercise price of the option. (provider: sec) |
| exercise_currency | The currency of the option exercise price. (provider: sec) |
| shares_per_contract | The number of shares per contract. (provider: sec) |
| delta | The delta of the option. (provider: sec) |
| rate_type_rec | The type of rate for reveivable portion of the swap. (provider: sec) |
| receive_currency | The receive currency of the swap. (provider: sec) |
| upfront_receive | The upfront amount received of the swap. (provider: sec) |
| floating_rate_index_rec | The floating rate index for reveivable portion of the swap. (provider: sec) |
| floating_rate_spread_rec | The floating rate spread for reveivable portion of the swap. (provider: sec) |
| rate_tenor_rec | The rate tenor for reveivable portion of the swap. (provider: sec) |
| rate_tenor_unit_rec | The rate tenor unit for reveivable portion of the swap. (provider: sec) |
| reset_date_rec | The reset date for reveivable portion of the swap. (provider: sec) |
| reset_date_unit_rec | The reset date unit for reveivable portion of the swap. (provider: sec) |
| rate_type_pmnt | The type of rate for payment portion of the swap. (provider: sec) |
| payment_currency | The payment currency of the swap. (provider: sec) |
| upfront_payment | The upfront amount received of the swap. (provider: sec) |
| floating_rate_index_pmnt | The floating rate index for payment portion of the swap. (provider: sec) |
| floating_rate_spread_pmnt | The floating rate spread for payment portion of the swap. (provider: sec) |
| rate_tenor_pmnt | The rate tenor for payment portion of the swap. (provider: sec) |
| rate_tenor_unit_pmnt | The rate tenor unit for payment portion of the swap. (provider: sec) |
| reset_date_pmnt | The reset date for payment portion of the swap. (provider: sec) |
| reset_date_unit_pmnt | The reset date unit for payment portion of the swap. (provider: sec) |
| repo_type | The type of repo. (provider: sec) |
| is_cleared | If the repo is cleared. (provider: sec) |
| is_tri_party | If the repo is tri party. (provider: sec) |
| principal_amount | The principal amount of the repo. (provider: sec) |
| principal_currency | The currency of the principal amount. (provider: sec) |
| collateral_type | The collateral type of the repo. (provider: sec) |
| collateral_amount | The collateral amount of the repo. (provider: sec) |
| collateral_currency | The currency of the collateral amount. (provider: sec) |
| exchange_currency | The currency of the exchange rate. (provider: sec) |
| exchange_rate | The exchange rate. (provider: sec) |
| currency_sold | The currency sold in a Forward Derivative. (provider: sec) |
| currency_amount_sold | The amount of currency sold in a Forward Derivative. (provider: sec) |
| currency_bought | The currency bought in a Forward Derivative. (provider: sec) |
| currency_amount_bought | The amount of currency bought in a Forward Derivative. (provider: sec) |
| notional_amount | The notional amount of the derivative. (provider: sec) |
| notional_currency | The currency of the derivative's notional amount. (provider: sec) |
| unrealized_gain | The unrealized gain or loss on the derivative. (provider: sec) |
