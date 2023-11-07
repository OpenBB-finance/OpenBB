---
title: Stock Insider Trading
description: This page provides in-depth details about Stock Insider Trading including
  data classes, parameters and structure. The content is a part of the official documentation
  for the OpenBB Provider Standard Models.
keywords:
- Docusaurus
- SEO
- Metadata
- Stock Insider Trading
- StockInsiderTradingData
- StockInsiderTradingQueryParams
- Symbol
- Transaction Type
- Filing Date
- Reporting CIK
- Securities Owned
- Type of Owner
- Acquisition or Disposition
- Securities Transacted
- Security Name
- Price
- Link
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Stock Insider Trading - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `StockInsiderTrading` | `StockInsiderTradingQueryParams` | `StockInsiderTradingData` |

### Import Statement

```python
from openbb_provider.standard_models.stock_insider_trading import (
StockInsiderTradingData,
StockInsiderTradingQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| transactionType | Union[List[Literal['A-Award', 'C-Conversion', 'D-Return', 'E-ExpireShort', 'F-InKind', 'G-Gift', 'H-ExpireLong', 'I-Discretionary', 'J-Other', 'L-Small', 'M-Exempt', 'O-OutOfTheMoney', 'P-Purchase', 'S-Sale', 'U-Tender', 'W-Will', 'X-InTheMoney', 'Z-Trust']], str] | Type of the transaction. | ['P-Purchase'] | True |
| page | int | Page number of the data to fetch. | 0 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

## Data

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol to get data for. |
| filing_date | datetime | Filing date of the stock insider trading. |
| transaction_date | date | Transaction date of the stock insider trading. |
| reporting_cik | int | Reporting CIK of the stock insider trading. |
| transaction_type | str | Transaction type of the stock insider trading. |
| securities_owned | int | Securities owned of the stock insider trading. |
| company_cik | int | Company CIK of the stock insider trading. |
| reporting_name | str | Reporting name of the stock insider trading. |
| type_of_owner | str | Type of owner of the stock insider trading. |
| acquisition_or_disposition | str | Acquisition or disposition of the stock insider trading. |
| form_type | str | Form type of the stock insider trading. |
| securities_transacted | float | Securities transacted of the stock insider trading. |
| price | float | Price of the stock insider trading. |
| security_name | str | Security name of the stock insider trading. |
| link | str | Link of the stock insider trading. |
</TabItem>

</Tabs>
