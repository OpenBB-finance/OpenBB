---
title: divs
description: OpenBB Platform Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# divs

Historical Dividends.

```python wordwrap
divs(symbol: Union[str, List[str]], provider: Union[Literal[str]] = fmp)
```

---

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Union[Literal['fmp']] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : List[HistoricalDividends]
        Serializable results.

    provider : Optional[Literal[Union[Literal['fmp'], NoneType]]
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
| date | date | Date of the historical dividends. |
| label | str | Label of the historical dividends. |
| adj_dividend | float | Adjusted dividend of the historical dividends. |
| dividend | float | Dividend of the historical dividends. |
| record_date | Union[date] | Record date of the historical dividends. |
| payment_date | Union[date] | Payment date of the historical dividends. |
| declaration_date | Union[date] | Declaration date of the historical dividends. |
</TabItem>

</Tabs>

