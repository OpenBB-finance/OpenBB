---
title: search
description: Learn how to search for ETFs with parameters like query, provider, exchange
  code, and more. Retrieve key details about ETFs, including market cap, industry,
  sector, beta, current price, annual dividend, trading volume, exchange, and country.
  Find actively trading ETFs and their symbol representation.
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



<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Search for ETFs.

An empty query returns the full list of ETFs from the provider.

```python wordwrap
obb.etf.search(query: str, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | Search query. |  | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| exchange | Literal['AMEX', 'NYSE', 'NASDAQ', 'ETF', 'TSX', 'EURONEXT'] | The exchange code the ETF trades on. | None | True |
| is_active | Literal[True, False] | Whether the ETF is actively trading. | None | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[EtfSearch]
        Serializable results.

    provider : Optional[Literal['fmp']]
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

</Tabs>

