---
title: pairs
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pairs

Forex Available Pairs.

```python wordwrap
pairs(provider: Union[Literal[str]] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Union[Literal['fmp', 'intrinio', 'polygon']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='polygon' label='polygon'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| provider | Union[Literal['fmp', 'intrinio', 'polygon']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| symbol | Union[str] | Symbol of the pair to search. | None | True |
| date | Union[date] | A specific date to get data for. | 2023-10-10 | True |
| search | Union[str] | Search for terms within the ticker and/or company name. |  | True |
| active | Union[bool] | Specify if the tickers returned should be actively traded on the queried date. | True | True |
| order | Union[Literal['asc', 'desc']] | Order data by ascending or descending. | asc | True |
| sort | Union[Literal['ticker', 'name', 'market', 'locale', 'currency_symbol', 'currency_name', 'base_currency_symbol', 'base_currency_name', 'last_updated_utc', 'delisted_utc']] | Sort field used for ordering. |  | True |
| limit | Union[typing_extensions.Annotated[int, Gt(gt=0)]] | The number of data entries to return. | 1000 | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[ForexPairs]
        Serializable results.

    provider : Optional[Literal[Union[Literal['fmp', 'intrinio', 'polygon'], NoneType]]
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
| name | str | Name of the currency pair. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| name | str | Name of the currency pair. |
| symbol | str | Symbol of the currency pair. |
| currency | str | Base currency of the currency pair. |
| stock_exchange | Union[str] | Stock exchange of the currency pair. |
| exchange_short_name | Union[str] | Short name of the stock exchange of the currency pair. |
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
| currency_symbol | Union[str] | The symbol of the quote currency. |
| currency_name | Union[str] | Name of the quote currency. |
| base_currency_symbol | Union[str] | The symbol of the base currency. |
| base_currency_name | Union[str] | Name of the base currency. |
| last_updated_utc | datetime | The last updated timestamp in UTC. |
| delisted_utc | Union[datetime] | The delisted timestamp in UTC. |
</TabItem>

</Tabs>

