---
title: ins
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ins

Stock Insider Trading.

```python wordwrap
ins(symbol: Union[str, List[str]], transactionType: List[Literal[list]] = ['P-Purchase'], reportingCik: int = None, companyCik: int = None, page: int = 0, provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| transactionType | List[Literal['A-Award', 'C-Conversion', 'D-Return', 'E-ExpireShort', 'F-InKind', 'G-Gift', 'H-ExpireLong', 'I-Discretionary', 'J-Other', 'L-Small', 'M-Exempt', 'O-OutOfTheMoney', 'P-Purchase', 'S-Sale', 'U-Tender', 'W-Will', 'X-InTheMoney', 'Z-Trust']] | Type of the transaction. | ['P-Purchase'] | True |
| reportingCik | int | CIK of the reporting owner. | None | True |
| companyCik | int | CIK of the company owner. | None | True |
| page | int | Page number of the data to fetch. | 0 | True |
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
| symbol | str | Symbol to get data for. |
| filing_date | datetime | Filing date of the stock insider trading. |
| transaction_date | date | Transaction date of the stock insider trading. |
| reporting_cik | int | Reporting CIK of the stock insider trading. |
| transaction_type | str | Transaction type of the stock insider trading. |
| securities_owned | int | Securities owned of the stock insider trading. |
| company_cik | int | Company CIK of the stock insider trading. |
| reporting_name | str | Reporting name of the stock insider trading. |
| type_of_owner | str | Type of owner of the stock insider trading. |
| acquistion_or_disposition | str | Acquistion or disposition of the stock insider trading. |
| form_type | str | Form type of the stock insider trading. |
| securities_transacted | float | Securities transacted of the stock insider trading. |
| price | float | Price of the stock insider trading. |
| security_name | str | Security name of the stock insider trading. |
| link | str | Link of the stock insider trading. |
</TabItem>

</Tabs>

