---
title: insider_trading
description: Learn how to use the stock insider trading Python function to get information
  about insider trading, including parameter details, return types, and data descriptions.
keywords:
- stock insider trading
- equity ownership
- Python function
- parameter details
- data description
- symbol
- transaction type
- limit
- provider
- returns
- results
- chart
- metadata
- data
- filing date
- transaction date
- reporting CIK
- securities owned
- company CIK
- reporting name
- type of owner
- acquisition or disposition
- form type
- securities transacted
- price
- security name
- link
---


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Stock Insider Trading. Information about insider trading.

```python wordwrap
obb.equity.ownership.insider_trading(symbol: Union[str, List[str]], transaction_type: Union[List[Literal[list]], str] = ['P-Purchase'], limit: int = 100, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| transaction_type | Union[List[Literal['A-Award', 'C-Conversion', 'D-Return', 'E-ExpireShort', 'F-InKind', 'G-Gift', 'H-ExpireLong', 'I-Discretionary', 'J-Other', 'L-Small', 'M-Exempt', 'O-OutOfTheMoney', 'P-Purchase', 'S-Sale', 'U-Tender', 'W-Will', 'X-InTheMoney', 'Z-Trust']], str] | Type of the transaction. | ['P-Purchase'] | True |
| limit | int | The number of data entries to return. | 100 | True |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[StockInsiderTrading]
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
| symbol | str | Symbol representing the entity requested in the data. |
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

