---
title: "search"
description: "Learn how to perform an equity search to find a company or stock ticker.  Understand the query parameters, such as search by ticker symbol and search provider.  Explore the various filters available, including market cap, price, beta, volume,  dividend, ETF, sector, industry, country, and exchange. Limit and structure the  results accordingly. Get access to the returned data, provider information, warnings,  chart, and metadata."
keywords:
- equity search
- company search
- stock ticker search
- query parameter
- search by ticker symbol
- search provider
- market cap filter
- price filter
- beta filter
- volume filter
- dividend filter
- ETF filter
- sector filter
- industry filter
- country filter
- exchange filter
- limit results
- data structure
- results
- provider
- warnings
- chart
- metadata
- symbol
- name
- dpm_name
- post_station
- market cap
- sector
- industry
- beta
- price
- last annual dividend
- volume
- exchange
- exchange_name
- country
- is_etf
- actively trading
- cik
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/search - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Search for stock symbol, CIK, LEI, or company name.


Examples
--------

```python
from openbb import obb
obb.equity.search(provider='intrinio')
obb.equity.search(query='AAPL', is_symbol=False, use_cache=True, provider='nasdaq')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| use_cache | bool | Whether to use the cache or not. | True | True |
| provider | Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| use_cache | bool | Whether to use the cache or not. | True | True |
| provider | Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| use_cache | bool | Whether to use the cache or not. | True | True |
| provider | Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| active | bool | When true, return companies that are actively traded (having stock prices within the past 14 days). When false, return companies that are not actively traded or never have been traded. | True | True |
| limit | int | The number of data entries to return. | 10000 | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| use_cache | bool | Whether to use the cache or not. | True | True |
| provider | Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| is_etf | bool | If True, returns ETFs. | None | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| use_cache | bool | Whether to use the cache or not. | True | True |
| provider | Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| is_fund | bool | Whether to direct the search to the list of mutual funds and ETFs. | False | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| use_cache | bool | Whether to use the cache or not. | True | True |
| provider | Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='tradier' label='tradier'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| use_cache | bool | Whether to use the cache or not. | True | True |
| provider | Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : EquitySearch
        Serializable results.
    provider : Literal['cboe', 'intrinio', 'nasdaq', 'sec', 'tmx', 'tradier']
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
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
</TabItem>

<TabItem value='cboe' label='cboe'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| dpm_name | str | Name of the primary market maker. |
| post_station | str | Post and station location on the CBOE trading floor. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| cik | str |  |
| lei | str | The Legal Entity Identifier (LEI) of the company. |
| intrinio_id | str | The Intrinio ID of the company. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| nasdaq_traded | str | Is Nasdaq traded? |
| exchange | str | Primary Exchange |
| market_category | str | Market Category |
| etf | str | Is ETF? |
| round_lot_size | float | Round Lot Size |
| test_issue | str | Is test Issue? |
| financial_status | str | Financial Status |
| cqs_symbol | str | CQS Symbol |
| nasdaq_symbol | str | NASDAQ Symbol |
| next_shares | str | Is NextShares? |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| cik | str | Central Index Key |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
</TabItem>

<TabItem value='tradier' label='tradier'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| exchange | str | Exchange where the security is listed. |
| security_type | Literal['stock', 'option', 'etf', 'index', 'mutual_fund'] | Type of security. |
</TabItem>

</Tabs>

