---
title: "dividends"
description: "Get historical dividends data for a given company with the OBB.equity.fundamental.dividends  function. Explore parameters like symbol and provider, and understand the returned  results, warnings, and metadata. View the data fields, including date, label, adj_dividend,  dividend, record_date, payment_date, and declaration_date."
keywords:
- historical dividends
- dividends data
- company dividends
- symbol
- data provider
- default provider
- results
- warnings
- chart
- metadata
- date
- label
- adj_dividend
- dividend
- record_date
- payment_date
- declaration_date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/fundamental/dividends - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get historical dividend data for a given company.


Examples
--------

```python
from openbb import obb
obb.equity.fundamental.dividends(symbol='AAPL', provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): nasdaq. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'nasdaq', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): nasdaq. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'nasdaq', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): nasdaq. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'nasdaq', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| limit | int | The number of data entries to return. | 100 | True |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): nasdaq. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'nasdaq', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): nasdaq. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'nasdaq', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): nasdaq. |  | False |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. | None | True |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. | None | True |
| provider | Literal['fmp', 'intrinio', 'nasdaq', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : HistoricalDividends
        Serializable results.
    provider : Literal['fmp', 'intrinio', 'nasdaq', 'tmx', 'yfinance']
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
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| amount | float | The dividend amount per share. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| amount | float | The dividend amount per share. |
| label | str | Label of the historical dividends. |
| adj_dividend | float | Adjusted dividend of the historical dividends. |
| record_date | date | Record date of the historical dividends. |
| payment_date | date | Payment date of the historical dividends. |
| declaration_date | date | Declaration date of the historical dividends. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| amount | float | The dividend amount per share. |
| factor | float | factor by which to multiply stock prices before this date, in order to calculate historically-adjusted stock prices. |
| currency | str | The currency in which the dividend is paid. |
| split_ratio | float | The ratio of the stock split, if a stock split occurred. |
</TabItem>

<TabItem value='nasdaq' label='nasdaq'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| amount | float | The dividend amount per share. |
| dividend_type | str | The type of dividend - i.e., cash, stock. |
| currency | str | The currency in which the dividend is paid. |
| record_date | date | The record date of ownership for eligibility. |
| payment_date | date | The payment date of the dividend. |
| declaration_date | date | Declaration date of the dividend. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| amount | float | The dividend amount per share. |
| currency | str | The currency the dividend is paid in. |
| decalaration_date | date | The date of the announcement. |
| record_date | date | The record date of ownership for rights to the dividend. |
| payment_date | date | The date the dividend is paid. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| ex_dividend_date | date | The ex-dividend date - the date on which the stock begins trading without rights to the dividend. |
| amount | float | The dividend amount per share. |
</TabItem>

</Tabs>

