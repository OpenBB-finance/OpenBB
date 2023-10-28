---
title: divs
description: A detailed documentation page outlining how to fetch historical dividends
  data for specific companies using the divs function. The page contains explanations
  on functions parameters, the return values, and the data that can be obtained.
keywords:
- Historical Dividends
- divs
- provider
- symbol
- data
- date
- label
- adjusted dividend
- dividend
- record date
- payment date
- declaration_date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="divs - Fa - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# divs

Historical Dividends. Historical dividends data for a given company.

```python wordwrap
divs(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
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
| date | date | Date of the historical dividends. |
| label | str | Label of the historical dividends. |
| adj_dividend | float | Adjusted dividend of the historical dividends. |
| dividend | float | Dividend of the historical dividends. |
| record_date | date | Record date of the historical dividends. |
| payment_date | date | Payment date of the historical dividends. |
| declaration_date | date | Declaration date of the historical dividends. |
</TabItem>

</Tabs>
