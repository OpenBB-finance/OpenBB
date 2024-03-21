---
title: "search"
description: "Learn how to search for available currency pairs using the `obb.currency.search`  function, and retrieve a list of results, including provider name, warnings, chart,  and metadata. Explore the various parameters such as provider, symbol, date, search  terms, active tickers, order data, sort field, and limit. Dive into the details  of the returned data, including name, symbol, currency, stock exchange, exchange  short name, code, base currency, quote currency, market, locale, currency symbol,  currency name, base currency symbol, base currency name, last updated timestamp  in UTC, and delisted timestamp in UTC."
keywords:
- currency search
- available currency pairs
- obb.currency.search
- provider
- symbol
- date
- search terms
- active tickers
- order data
- sort field
- limit
- results
- warnings
- chart
- metadata
- name
- symbol
- currency
- stock exchange
- exchange short name
- code
- base currency
- quote currency
- market
- locale
- currency symbol
- currency name
- base currency symbol
- base currency name
- last updated utc
- delisted utc
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="currency/search - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Currency Search.

Search available currency pairs.
Currency pairs are the national currencies from two countries coupled for trading on
the foreign exchange (FX) marketplace.
Both currencies will have exchange rates on which the trade will have its position basis.
All trading within the forex market, whether selling, buying, or trading, will take place through currency pairs.
(ref: Investopedia)
Major currency pairs include pairs such as EUR/USD, USD/JPY, GBP/USD, etc.


Examples
--------

```python
from openbb import obb
obb.currency.search(provider='intrinio')
# Search for 'EURUSD' currency pair using 'intrinio' as provider.
obb.currency.search(provider='intrinio', symbol=EURUSD)
# Search for actively traded currency pairs on the queried date using 'polygon' as provider.
obb.currency.search(provider='polygon', date=2024-01-02, active=True)
# Search for terms  using 'polygon' as provider.
obb.currency.search(provider='polygon', search=Euro zone)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'intrinio', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| symbol | str | Symbol of the pair to search. | None | True |
| date | Union[date, str] | A specific date to get data for. | None | True |
| search | str | Search for terms within the ticker and/or company name. |  | True |
| active | bool | Specify if the tickers returned should be actively traded on the queried date. | True | True |
| order | Literal['asc', 'desc'] | Order data by ascending or descending. | asc | True |
| sort | Literal['ticker', 'name', 'market', 'locale', 'currency_symbol', 'currency_name', 'base_currency_symbol', 'base_currency_name', 'last_updated_utc', 'delisted_utc'] | Sort field used for ordering. |  | True |
| limit | int, Gt(gt=0) | The number of data entries to return. | 1000 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : CurrencyPairs
        Serializable results.
    provider : Literal['fmp', 'intrinio', 'polygon']
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
| name | str | Name of the currency pair. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the currency pair. |
| symbol | str | Symbol of the currency pair. |
| currency | str | Base currency of the currency pair. |
| stock_exchange | str | Stock exchange of the currency pair. |
| exchange_short_name | str | Short name of the stock exchange of the currency pair. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the currency pair. |
| code | str | Code of the currency pair. |
| base_currency | str | ISO 4217 currency code of the base currency. |
| quote_currency | str | ISO 4217 currency code of the quote currency. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the currency pair. |
| market | str | Name of the trading market. Always 'fx'. |
| locale | str | Locale of the currency pair. |
| currency_symbol | str | The symbol of the quote currency. |
| currency_name | str | Name of the quote currency. |
| base_currency_symbol | str | The symbol of the base currency. |
| base_currency_name | str | Name of the base currency. |
| last_updated_utc | datetime | The last updated timestamp in UTC. |
| delisted_utc | datetime | The delisted timestamp in UTC. |
</TabItem>

</Tabs>

