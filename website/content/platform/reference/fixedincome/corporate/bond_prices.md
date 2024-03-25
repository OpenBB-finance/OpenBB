---
title: "bond_prices"
description: "Corporate Bond Prices"
keywords:
- fixedincome
- corporate
- bond_prices
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome/corporate/bond_prices - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Corporate Bond Prices.


Examples
--------

```python
from openbb import obb
obb.fixedincome.corporate.bond_prices(provider='tmx')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | The country to get data. Matches partial name. | None | True |
| issuer_name | str | Name of the issuer. Returns partial matches and is case insensitive. | None | True |
| isin | Union[List, str] | International Securities Identification Number(s) of the bond(s). | None | True |
| lei | str | Legal Entity Identifier of the issuing entity. | None | True |
| currency | Union[List, str] | Currency of the bond. Formatted as the 3-letter ISO 4217 code (e.g. GBP, EUR, USD). | None | True |
| coupon_min | float | Minimum coupon rate of the bond. | None | True |
| coupon_max | float | Maximum coupon rate of the bond. | None | True |
| issued_amount_min | int | Minimum issued amount of the bond. | None | True |
| issued_amount_max | str | Maximum issued amount of the bond. | None | True |
| maturity_date_min | date | Minimum maturity date of the bond. | None | True |
| maturity_date_max | date | Maximum maturity date of the bond. | None | True |
| provider | Literal['tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | The country to get data. Matches partial name. | None | True |
| issuer_name | str | Name of the issuer. Returns partial matches and is case insensitive. | None | True |
| isin | Union[List, str] | International Securities Identification Number(s) of the bond(s). | None | True |
| lei | str | Legal Entity Identifier of the issuing entity. | None | True |
| currency | Union[List, str] | Currency of the bond. Formatted as the 3-letter ISO 4217 code (e.g. GBP, EUR, USD). | None | True |
| coupon_min | float | Minimum coupon rate of the bond. | None | True |
| coupon_max | float | Maximum coupon rate of the bond. | None | True |
| issued_amount_min | int | Minimum issued amount of the bond. | None | True |
| issued_amount_max | str | Maximum issued amount of the bond. | None | True |
| maturity_date_min | date | Minimum maturity date of the bond. | None | True |
| maturity_date_max | date | Maximum maturity date of the bond. | None | True |
| provider | Literal['tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'tmx' if there is no default. | tmx | True |
| issue_date_min | date | Filter by the minimum original issue date. | None | True |
| issue_date_max | date | Filter by the maximum original issue date. | None | True |
| last_traded_min | date | Filter by the minimum last trade date. | None | True |
| use_cache | bool | All bond data is sourced from a single JSON file that is updated daily. The file is cached for one day to eliminate downloading more than once. Caching will significantly speed up subsequent queries. To bypass, set to False. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : BondPrices
        Serializable results.
    provider : Literal['tmx']
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
| isin | str | International Securities Identification Number of the bond. |
| lei | str | Legal Entity Identifier of the issuing entity. |
| figi | str | FIGI of the bond. |
| cusip | str | CUSIP of the bond. |
| coupon_rate | float | Coupon rate of the bond. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| isin | str | International Securities Identification Number of the bond. |
| lei | str | Legal Entity Identifier of the issuing entity. |
| figi | str | FIGI of the bond. |
| cusip | str | CUSIP of the bond. |
| coupon_rate | float | Coupon rate of the bond. |
| ytm | float | Yield to maturity (YTM) is the rate of return anticipated on a bond if it is held until the maturity date. It takes into account the current market price, par value, coupon rate and time to maturity. It is assumed that all coupons are reinvested at the same rate. Values are returned as a normalized percent. |
| price | float | The last price for the bond. |
| highest_price | float | The highest price for the bond on the last traded date. |
| lowest_price | float | The lowest price for the bond on the last traded date. |
| total_trades | int | Total number of trades on the last traded date. |
| last_traded_date | date | Last traded date of the bond. |
| maturity_date | date | Maturity date of the bond. |
| issue_date | date | Issue date of the bond. This is the date when the bond first accrues interest. |
| issuer_name | str | Name of the issuing entity. |
</TabItem>

</Tabs>

