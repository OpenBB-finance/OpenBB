---
title: ForexPairs
description: OpenBB Platform Data Model
---


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Literal['fmp', 'polygon'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol of the pair to search. |  | True |
| date | date | A specific date to get data for. | 2023-09-06 | True |
| search | str | Search for terms within the ticker and/or company name. |  | True |
| active | Literal[True, False] | Specify if the tickers returned should be actively traded on the queried date. | True | True |
| order | Literal['asc', 'desc'] | Order data by ascending or descending. | asc | True |
| sort | Literal['ticker', 'name', 'market', 'locale', 'currency_symbol', 'currency_name', 'base_currency_symbol', 'base_currency_name', 'last_updated_utc', 'delisted_utc'] | Sort field used for ordering. |  | True |
| limit | PositiveInt | The number of data entries to return. | 1000 | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the currency pair. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol of the currency pair. |
| currency | str | Base currency of the currency pair. |
| stockExchange | str | Stock exchange of the currency pair. |
| exchange_short_name | str | Short name of the stock exchange of the currency pair. |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| market | str | The name of the trading market. Always 'fx'. |
| locale | str | The locale of the currency pair. |
| currency_symbol | str | The symbol of the quote currency. |
| currency_name | str | The name of the quote currency. |
| base_currency_symbol | str | The symbol of the base currency. |
| base_currency_name | str | The name of the base currency. |
| last_updated_utc | datetime | The last updated timestamp in UTC. |
| delisted_utc | datetime | The delisted timestamp in UTC. |
</TabItem>

</Tabs>

