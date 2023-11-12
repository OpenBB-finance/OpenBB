---
title: dividends
description: Get historical dividends data for a given company with the OBB.equity.fundamental.dividends
  function. Explore parameters like symbol and provider, and understand the returned
  results, warnings, and metadata. View the data fields, including date, label, adj_dividend,
  dividend, record_date, payment_date, and declaration_date.
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


<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Historical Dividends. Historical dividends data for a given company.

```python wordwrap
obb.equity.fundamental.dividends(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[HistoricalDividends]
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
| date | date | The date of the data. |
| label | str | Label of the historical dividends. |
| adj_dividend | float | Adjusted dividend of the historical dividends. |
| dividend | float | Dividend of the historical dividends. |
| record_date | date | Record date of the historical dividends. |
| payment_date | date | Payment date of the historical dividends. |
| declaration_date | date | Declaration date of the historical dividends. |
</TabItem>

</Tabs>

