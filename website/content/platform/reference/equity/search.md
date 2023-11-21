---
title: search
description: Learn how to perform an equity search to find a company or stock ticker.
  Understand the query parameters, such as search by ticker symbol and search provider.
  Explore the various filters available, including market cap, price, beta, volume,
  dividend, ETF, sector, industry, country, and exchange. Limit and structure the
  results accordingly. Get access to the returned data, provider information, warnings,
  chart, and metadata.
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

<HeadTitle title="equity /search - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Equity Search. Search for a company or stock ticker.

```python wordwrap
obb.equity.search(query: str, is_symbol: bool = False, provider: Literal[str] = cboe)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe', 'sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
</TabItem>

<TabItem value='sec' label='sec'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| is_symbol | bool | Whether to search by ticker symbol. | False | True |
| provider | Literal['cboe', 'sec'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'cboe' if there is no default. | cboe | True |
| is_fund | bool | Whether to direct the search to the list of mutual funds and ETFs. | False | True |
| use_cache | bool | Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days. | True | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EquitySearch]
        Serializable results.

    provider : Optional[Literal['cboe', 'sec']]
        Provider name.

    warnings : Optional[List[Warning_]]
        List of warnings.

    chart : Optional[Chart]
        Chart object.

    metadata: Optional[Metadata]
        Metadata info about the command execution.
```

---

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

<TabItem value='sec' label='sec'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Name of the company. |
| cik | str | Central Index Key |
</TabItem>

</Tabs>

