---
title: "Treasury Prices"
description: "Government Treasury Prices by date"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `TreasuryPrices` | `TreasuryPricesQueryParams` | `TreasuryPricesData` |

### Import Statement

```python
from openbb_core.provider.standard_models.treasury_prices import (
TreasuryPricesData,
TreasuryPricesQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. No date will return the current posted data. | None | True |
| provider | Literal['government_us', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'government_us' if there is no default. | government_us | True |
</TabItem>

<TabItem value='government_us' label='government_us'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. No date will return the current posted data. | None | True |
| provider | Literal['government_us', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'government_us' if there is no default. | government_us | True |
| cusip | str | Filter by CUSIP. | None | True |
| security_type | Literal[None, 'bill', 'note', 'bond', 'tips', 'frn'] | Filter by security type. | None | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | Union[date, str] | A specific date to get data for. No date will return the current posted data. | None | True |
| provider | Literal['government_us', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'government_us' if there is no default. | government_us | True |
| govt_type | Literal['federal', 'provincial', 'municipal'] | The level of government issuer. | federal | True |
| issue_date_min | date | Filter by the minimum original issue date. | None | True |
| issue_date_max | date | Filter by the maximum original issue date. | None | True |
| last_traded_min | date | Filter by the minimum last trade date. | None | True |
| maturity_date_min | date | Filter by the minimum maturity date. | None | True |
| maturity_date_max | date | Filter by the maximum maturity date. | None | True |
| use_cache | bool | All bond data is sourced from a single JSON file that is updated daily. The file is cached for one day to eliminate downloading more than once. Caching will significantly speed up subsequent queries. To bypass, set to False. | True | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| issuer_name | str | Name of the issuing entity. |
| cusip | str | CUSIP of the security. |
| isin | str | ISIN of the security. |
| security_type | str | The type of Treasury security - i.e., Bill, Note, Bond, TIPS, FRN. |
| issue_date | date | The original issue date of the security. |
| maturity_date | date | The maturity date of the security. |
| call_date | date | The call date of the security. |
| bid | float | The bid price of the security. |
| offer | float | The offer price of the security. |
| eod_price | float | The end-of-day price of the security. |
| last_traded_date | date | The last trade date of the security. |
| total_trades | int | Total number of trades on the last traded date. |
| last_price | float | The last price of the security. |
| highest_price | float | The highest price for the bond on the last traded date. |
| lowest_price | float | The lowest price for the bond on the last traded date. |
| rate | float | The annualized interest rate or coupon of the security. |
| ytm | float | Yield to maturity (YTM) is the rate of return anticipated on a bond if it is held until the maturity date. It takes into account the current market price, par value, coupon rate and time to maturity. It is assumed that all coupons are reinvested at the same rate. |
</TabItem>

<TabItem value='government_us' label='government_us'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| issuer_name | str | Name of the issuing entity. |
| cusip | str | CUSIP of the security. |
| isin | str | ISIN of the security. |
| security_type | str | The type of Treasury security - i.e., Bill, Note, Bond, TIPS, FRN. |
| issue_date | date | The original issue date of the security. |
| maturity_date | date | The maturity date of the security. |
| call_date | date | The call date of the security. |
| bid | float | The bid price of the security. |
| offer | float | The offer price of the security. |
| eod_price | float | The end-of-day price of the security. |
| last_traded_date | date | The last trade date of the security. |
| total_trades | int | Total number of trades on the last traded date. |
| last_price | float | The last price of the security. |
| highest_price | float | The highest price for the bond on the last traded date. |
| lowest_price | float | The lowest price for the bond on the last traded date. |
| rate | float | The annualized interest rate or coupon of the security. |
| ytm | float | Yield to maturity (YTM) is the rate of return anticipated on a bond if it is held until the maturity date. It takes into account the current market price, par value, coupon rate and time to maturity. It is assumed that all coupons are reinvested at the same rate. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| issuer_name | str | Name of the issuing entity. |
| cusip | str | CUSIP of the security. |
| isin | str | ISIN of the security. |
| security_type | str | The type of Treasury security - i.e., Bill, Note, Bond, TIPS, FRN. |
| issue_date | date | The original issue date of the security. |
| maturity_date | date | The maturity date of the security. |
| call_date | date | The call date of the security. |
| bid | float | The bid price of the security. |
| offer | float | The offer price of the security. |
| eod_price | float | The end-of-day price of the security. |
| last_traded_date | date | The last trade date of the security. |
| total_trades | int | Total number of trades on the last traded date. |
| last_price | float | The last price of the security. |
| highest_price | float | The highest price for the bond on the last traded date. |
| lowest_price | float | The lowest price for the bond on the last traded date. |
| rate | float | The annualized interest rate or coupon of the security. |
| ytm | float | Yield to maturity (YTM) is the rate of return anticipated on a bond if it is held until the maturity date. It takes into account the current market price, par value, coupon rate and time to maturity. It is assumed that all coupons are reinvested at the same rate. |
</TabItem>

</Tabs>

