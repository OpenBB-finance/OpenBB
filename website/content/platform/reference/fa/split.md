---
title: split
description: Page providing detailed documentation about Historical Stock Splits function
  in our API. Contains information about parameters such as stock symbol and data
  provider, return values, and detailed data descriptions. The page is particularly
  useful for finance professionals and developers interacting with finance APIs.
keywords:
- Historical Stock Splits
- Stock data
- Stock split data
- SEO for Finance
- Stock Symbols
- Stock Market
- Market Data
- Python Code
- Data Providers
- Finance API
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fa.split - Reference | OpenBB Platform Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# split

Historical Stock Splits. Historical stock splits data.

```python wordwrap
split(symbol: Union[str, List[str]], provider: Literal[str] = fmp)
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
    results : List[HistoricalStockSplits]
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
| label | str | Label of the historical stock splits. |
| numerator | float | Numerator of the historical stock splits. |
| denominator | float | Denominator of the historical stock splits. |
</TabItem>

</Tabs>
