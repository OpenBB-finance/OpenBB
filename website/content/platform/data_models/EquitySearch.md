---
title: Equity Search
description: OpenBB Platform Data Model
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EquitySearch` | `EquitySearchQueryParams` | `EquitySearchData` |

### Import Statement

```python
from openbb_core.provider.standard_models.equity_search import (
EquitySearchData,
EquitySearchQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe', 'fmp', 'sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe', 'fmp', 'sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| mktcap_min | int | Filter by market cap greater than this value. | None | True |
| mktcap_max | int | Filter by market cap less than this value. | None | True |
| price_min | float | Filter by price greater than this value. | None | True |
| price_max | float | Filter by price less than this value. | None | True |
| beta_min | float | Filter by a beta greater than this value. | None | True |
| beta_max | float | Filter by a beta less than this value. | None | True |
| volume_min | int | Filter by volume greater than this value. | None | True |
| volume_max | int | Filter by volume less than this value. | None | True |
| dividend_min | float | Filter by dividend amount greater than this value. | None | True |
| dividend_max | float | Filter by dividend amount less than this value. | None | True |
| is_etf | bool | If true, returns only ETFs. | False | True |
| is_active | bool | If false, returns only inactive tickers. | True | True |
| sector | Literal['Consumer Cyclical', 'Energy', 'Technology', 'Industrials', 'Financial Services', 'Basic Materials', 'Communication Services', 'Consumer Defensive', 'Healthcare', 'Real Estate', 'Utilities', 'Industrial Goods', 'Financial', 'Services', 'Conglomerates'] | Filter by sector. | None | True |
| industry | str | Filter by industry. | None | True |
| country | str | Filter by country, as a two-letter country code. | None | True |
| exchange | Literal['amex', 'ase', 'asx', 'ath', 'bme', 'bru', 'bud', 'bue', 'cai', 'cnq', 'cph', 'dfm', 'doh', 'etf', 'euronext', 'hel', 'hkse', 'ice', 'iob', 'ist', 'jkt', 'jnb', 'jpx', 'kls', 'koe', 'ksc', 'kuw', 'lse', 'mex', 'nasdaq', 'neo', 'nse', 'nyse', 'nze', 'osl', 'otc', 'pnk', 'pra', 'ris', 'sao', 'sau', 'set', 'sgo', 'shh', 'shz', 'six', 'sto', 'tai', 'tlv', 'tsx', 'two', 'vie', 'wse', 'xetra'] | Filter by exchange. | None | True |
| limit | int | Limit the number of results to return. | 50000 | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe', 'fmp', 'sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| is_fund | bool | Whether to direct the search to the list of mutual funds and ETFs. | False | True |
| use_cache | bool | Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days. | True | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

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

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| market_cap | int | The market cap of ticker. |
| sector | str | The sector the ticker belongs to. |
| industry | str | The industry ticker belongs to. |
| beta | float | The beta of the ETF. |
| price | float | The current price. |
| last_annual_dividend | float | The last annual amount dividend paid. |
| volume | int | The current trading volume. |
| exchange | str | The exchange code the asset trades on. |
| exchange_name | str | The full name of the primary exchange. |
| country | str | The two-letter country abbreviation where the head office is located. |
| is_etf | Literal[True, False] | Whether the ticker is an ETF. |
| actively_trading | Literal[True, False] | Whether the ETF is actively trading. |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| cik | str | Central Index Key |
</TabItem>

</Tabs>
