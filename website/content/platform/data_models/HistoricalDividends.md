---
title: Historical Dividends
description: Documentation page about implementation details of historical dividends
  in OpenBB Provider. The page dives into class names, import statement, parameters,
  and data.
keywords:
- OpenBB Provider
- Historical Dividends
- Parameters
- Data
- Python
- Import Statement
- HistoricalDividendsQueryParams
- HistoricalDividendsData
- fmp provider
- Dividends
- Date
- Label
- Adj Dividend
- Dividend
- Record Date
- Payment Date
- Declaration Date
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Historical Dividends - Data_Models | OpenBB Platform Docs" />


import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';


---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `HistoricalDividends` | `HistoricalDividendsQueryParams` | `HistoricalDividendsData` |

### Import Statement

```python
from openbb_provider.standard_models.historical_dividends import (
HistoricalDividendsData,
HistoricalDividendsQueryParams,
)
```

## Parameters

<Tabs>
<TabItem value="standard" label="Standard">

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. |  | False |
| provider | Literal['fmp'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

</Tabs>

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
