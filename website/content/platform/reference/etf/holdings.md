---
title: "holdings"
description: "Learn how to get the holdings data for an individual ETF using the `obb.etf.holdings`  method. Understand the parameters like symbol, provider, date, and CIK. Explore  the returns, results, warnings, chart, and metadata. Dive into the data fields like  symbol, name, LEI, title, CUSIP, ISIN, balance, units, currency, value, weight,  payoff profile, asset category, issuer category, country, and more."
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

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/holdings - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get the holdings for an individual ETF.


Examples
--------

```python
from openbb import obb
obb.etf.holdings(symbol='XLK', provider='fmp')
# Including a date (FMP, SEC) will return the holdings as per NPORT-P filings.
obb.etf.holdings(symbol='XLK', date=2022-03-31, provider='fmp')
# The same data can be returned from the SEC directly.
obb.etf.holdings(symbol='XLK', date=2022-03-31, provider='sec')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp', 'sec', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp', 'sec', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| date | Union[Union[str, date], str] | A specific date to get data for. Entering a date will attempt to return the NPORT-P filing for the entered date. This needs to be _exactly_ the date of the filing. Use the holdings_date command/endpoint to find available filing dates for the ETF. | None | True |
| cik | str | The CIK of the filing entity. Overrides symbol. | None | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp', 'sec', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| date | Union[Union[str, date], str] | A specific date to get data for. The date represents the period ending. The date entered will return the closest filing. | None | True |
| use_cache | bool | Whether or not to use cache for the request. | True | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. (ETF) |  | False |
| provider | Literal['fmp', 'sec', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| use_cache | bool | Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EtfHoldings
        Serializable results.
    provider : Literal['fmp', 'sec', 'tmx']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF holding. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF holding. |
| lei | str | The LEI of the holding. |
| title | str | The title of the holding. |
| cusip | str | The CUSIP of the holding. |
| isin | str | The ISIN of the holding. |
| balance | int | The balance of the holding, in shares or units. |
| units | Union[str, float] | The type of units. |
| currency | str | The currency of the holding. |
| value | float | The value of the holding, in dollars. |
| weight | float | The weight of the holding, as a normalized percent. |
| payoff_profile | str | The payoff profile of the holding. |
| asset_category | str | The asset category of the holding. |
| issuer_category | str | The issuer category of the holding. |
| country | str | The country of the holding. |
| is_restricted | str | Whether the holding is restricted. |
| fair_value_level | int | The fair value level of the holding. |
| is_cash_collateral | str | Whether the holding is cash collateral. |
| is_non_cash_collateral | str | Whether the holding is non-cash collateral. |
| is_loan_by_fund | str | Whether the holding is loan by fund. |
| cik | str | The CIK of the filing. |
| acceptance_datetime | str | The acceptance datetime of the filing. |
| updated | Union[date, datetime] | The date the data was updated. |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF holding. |
| lei | str | The LEI of the holding. |
| cusip | str | The CUSIP of the holding. |
| isin | str | The ISIN of the holding. |
| other_id | str | Internal identifier for the holding. |
| balance | float | The balance of the holding. |
| weight | float | The weight of the holding in ETF in %. |
| value | float | The value of the holding in USD. |
| payoff_profile | str | The payoff profile of the holding. |
| units | Union[str, float] | The units of the holding. |
| currency | str | The currency of the holding. |
| asset_category | str | The asset category of the holding. |
| issuer_category | str | The issuer category of the holding. |
| country | str | The country of the holding. |
| is_restricted | str | Whether the holding is restricted. |
| fair_value_level | int | The fair value level of the holding. |
| is_cash_collateral | str | Whether the holding is cash collateral. |
| is_non_cash_collateral | str | Whether the holding is non-cash collateral. |
| is_loan_by_fund | str | Whether the holding is loan by fund. |
| loan_value | float | The loan value of the holding. |
| issuer_conditional | str | The issuer conditions of the holding. |
| asset_conditional | str | The asset conditions of the holding. |
| maturity_date | date | The maturity date of the debt security. |
| coupon_kind | str | The type of coupon for the debt security. |
| rate_type | str | The type of rate for the debt security, floating or fixed. |
| annualized_return | float | The annualized return on the debt security. |
| is_default | str | If the debt security is defaulted. |
| in_arrears | str | If the debt security is in arrears. |
| is_paid_kind | str | If the debt security payments are paid in kind. |
| derivative_category | str | The derivative category of the holding. |
| counterparty | str | The counterparty of the derivative. |
| underlying_name | str | The name of the underlying asset associated with the derivative. |
| option_type | str | The type of option. |
| derivative_payoff | str | The payoff profile of the derivative. |
| expiry_date | date | The expiry or termination date of the derivative. |
| exercise_price | float | The exercise price of the option. |
| exercise_currency | str | The currency of the option exercise price. |
| shares_per_contract | float | The number of shares per contract. |
| delta | Union[str, float] | The delta of the option. |
| rate_type_rec | str | The type of rate for reveivable portion of the swap. |
| receive_currency | str | The receive currency of the swap. |
| upfront_receive | float | The upfront amount received of the swap. |
| floating_rate_index_rec | str | The floating rate index for reveivable portion of the swap. |
| floating_rate_spread_rec | float | The floating rate spread for reveivable portion of the swap. |
| rate_tenor_rec | str | The rate tenor for reveivable portion of the swap. |
| rate_tenor_unit_rec | Union[int, str] | The rate tenor unit for reveivable portion of the swap. |
| reset_date_rec | str | The reset date for reveivable portion of the swap. |
| reset_date_unit_rec | Union[int, str] | The reset date unit for reveivable portion of the swap. |
| rate_type_pmnt | str | The type of rate for payment portion of the swap. |
| payment_currency | str | The payment currency of the swap. |
| upfront_payment | float | The upfront amount received of the swap. |
| floating_rate_index_pmnt | str | The floating rate index for payment portion of the swap. |
| floating_rate_spread_pmnt | float | The floating rate spread for payment portion of the swap. |
| rate_tenor_pmnt | str | The rate tenor for payment portion of the swap. |
| rate_tenor_unit_pmnt | Union[int, str] | The rate tenor unit for payment portion of the swap. |
| reset_date_pmnt | str | The reset date for payment portion of the swap. |
| reset_date_unit_pmnt | Union[int, str] | The reset date unit for payment portion of the swap. |
| repo_type | str | The type of repo. |
| is_cleared | str | If the repo is cleared. |
| is_tri_party | str | If the repo is tri party. |
| principal_amount | float | The principal amount of the repo. |
| principal_currency | str | The currency of the principal amount. |
| collateral_type | str | The collateral type of the repo. |
| collateral_amount | float | The collateral amount of the repo. |
| collateral_currency | str | The currency of the collateral amount. |
| exchange_currency | str | The currency of the exchange rate. |
| exchange_rate | float | The exchange rate. |
| currency_sold | str | The currency sold in a Forward Derivative. |
| currency_amount_sold | float | The amount of currency sold in a Forward Derivative. |
| currency_bought | str | The currency bought in a Forward Derivative. |
| currency_amount_bought | float | The amount of currency bought in a Forward Derivative. |
| notional_amount | float | The notional amount of the derivative. |
| notional_currency | str | The currency of the derivative's notional amount. |
| unrealized_gain | float | The unrealized gain or loss on the derivative. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. (ETF) |
| name | str | Name of the ETF holding. |
| weight | float | The weight of the asset in the portfolio, as a normalized percentage. |
| shares | Union[int, str] | The value of the assets under management. |
| market_value | Union[str, float] | The market value of the holding. |
| currency | str | The currency of the holding. |
| share_percentage | float | The share percentage of the holding, as a normalized percentage. |
| share_change | Union[str, float] | The change in shares of the holding. |
| country | str | The country of the holding. |
| exchange | str | The exchange code of the holding. |
| type_id | str | The holding type ID of the asset. |
| fund_id | str | The fund ID of the asset. |
</TabItem>

</Tabs>

