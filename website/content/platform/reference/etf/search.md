---
title: "search"
description: "Learn how to search for ETFs with parameters like query, provider, exchange  code, and more. Retrieve key details about ETFs, including market cap, industry,  sector, beta, current price, annual dividend, trading volume, exchange, and country.  Find actively trading ETFs and their symbol representation."
keywords:
- search for ETFs
- ETF search query
- ETF provider
- ETF exchange code
- ETF trading volume
- ETF market cap
- ETF sector
- ETF industry
- ETF beta
- ETF current price
- ETF annual dividend
- ETF exchange
- ETF country
- actively trading ETF
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/search - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Search for ETFs.

An empty query returns the full list of ETFs from the provider.


Examples
--------

```python
from openbb import obb
# An empty query returns the full list of ETFs from the provider.
obb.etf.search(provider='fmp')
# The query will return results from text-based fields containing the term.
obb.etf.search(query='commercial real estate', provider='fmp')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp', 'intrinio', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp', 'intrinio', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| exchange | Literal['AMEX', 'NYSE', 'NASDAQ', 'ETF', 'TSX', 'EURONEXT'] | The exchange code the ETF trades on. | None | True |
| is_active | Literal[True, False] | Whether the ETF is actively trading. | None | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp', 'intrinio', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| exchange | Literal['xnas', 'arcx', 'bats', 'xnys', 'bvmf', 'xshg', 'xshe', 'xhkg', 'xbom', 'xnse', 'xidx', 'tase', 'xkrx', 'xkls', 'xmex', 'xses', 'roco', 'xtai', 'xbkk', 'xist'] | Target a specific exchange by providing the MIC code. | None | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp', 'intrinio', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| div_freq | Literal['monthly', 'annually', 'quarterly'] | The dividend payment frequency. | None | True |
| sort_by | Literal['nav', 'return_1m', 'return_3m', 'return_6m', 'return_1y', 'return_3y', 'return_ytd', 'beta_1y', 'volume_avg_daily', 'management_fee', 'distribution_yield', 'pb_ratio', 'pe_ratio'] | The column to sort by. | None | True |
| use_cache | bool | Whether to use a cached request. All ETF data comes from a single JSON file that is updated daily. To bypass, set to False. If True, the data will be cached for 4 hours. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EtfSearch
        Serializable results.
    provider : Literal['fmp', 'intrinio', 'tmx']
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
| symbol | str | Symbol representing the entity requested in the data.(ETF) |
| name | str | Name of the ETF. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data.(ETF) |
| name | str | Name of the ETF. |
| market_cap | float | The market cap of the ETF. |
| sector | str | The sector of the ETF. |
| industry | str | The industry of the ETF. |
| beta | float | The beta of the ETF. |
| price | float | The current price of the ETF. |
| last_annual_dividend | float | The last annual dividend paid. |
| volume | float | The current trading volume of the ETF. |
| exchange | str | The exchange code the ETF trades on. |
| exchange_name | str | The full name of the exchange the ETF trades on. |
| country | str | The country the ETF is registered in. |
| actively_trading | Literal[True, False] | Whether the ETF is actively trading. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data.(ETF) |
| name | str | Name of the ETF. |
| exchange | str | The exchange MIC code. |
| figi_ticker | str | The OpenFIGI ticker. |
| ric | str | The Reuters Instrument Code. |
| isin | str | The International Securities Identification Number. |
| sedol | str | The Stock Exchange Daily Official List. |
| intrinio_id | str | The unique Intrinio ID for the security. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data.(ETF) |
| name | str | Name of the ETF. |
| short_name | str | The short name of the ETF. |
| inception_date | str | The inception date of the ETF. |
| issuer | str | The issuer of the ETF. |
| investment_style | str | The investment style of the ETF. |
| esg | bool | Whether the ETF qualifies as an ESG fund. |
| currency | str | The currency of the ETF. |
| unit_price | float | The unit price of the ETF. |
| close | float | The closing price of the ETF. |
| prev_close | float | The previous closing price of the ETF. |
| return_1m | float | The one-month return of the ETF, as a normalized percent. |
| return_3m | float | The three-month return of the ETF, as a normalized percent. |
| return_6m | float | The six-month return of the ETF, as a normalized percent. |
| return_ytd | float | The year-to-date return of the ETF, as a normalized percent. |
| return_1y | float | The one-year return of the ETF, as a normalized percent. |
| beta_1y | float | The one-year beta of the ETF, as a normalized percent. |
| return_3y | float | The three-year return of the ETF, as a normalized percent. |
| beta_3y | float | The three-year beta of the ETF, as a normalized percent. |
| return_5y | float | The five-year return of the ETF, as a normalized percent. |
| beta_5y | float | The five-year beta of the ETF, as a normalized percent. |
| return_10y | float | The ten-year return of the ETF, as a normalized percent. |
| beta_10y | float | The ten-year beta of the ETF. |
| beta_15y | float | The fifteen-year beta of the ETF. |
| return_from_inception | float | The return from inception of the ETF, as a normalized percent. |
| avg_volume | int | The average daily volume of the ETF. |
| avg_volume_30d | int | The 30-day average volume of the ETF. |
| aum | float | The AUM of the ETF. |
| pe_ratio | float | The price-to-earnings ratio of the ETF. |
| pb_ratio | float | The price-to-book ratio of the ETF. |
| management_fee | float | The management fee of the ETF, as a normalized percent. |
| mer | float | The management expense ratio of the ETF, as a normalized percent. |
| distribution_yield | float | The distribution yield of the ETF, as a normalized percent. |
| dividend_frequency | str | The dividend payment frequency of the ETF. |
</TabItem>

</Tabs>

