---
title: search
description: The documentation page details the 'search' function of the OpenBB python
  library used for querying stocks information. The function allows queries based
  on parameters like country, sector, industry and exchange country. The search results
  are returned as a pandas DataFrame.
keywords:
- search
- query
- tickers
- stocks
- country
- sector
- industry
- exchange_country
- limit
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.search - Reference | OpenBB SDK Docs" />

Search selected query for tickers.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L98)]

```python
openbb.stocks.search(query: str = "", country: str = "", sector: str = "", industry: str = "", exchange_country: str = "", limit: int = 0)
```

---

## Parameters

| Name             | Type | Description                                             | Default | Optional |
|------------------|------|---------------------------------------------------------|---------|----------|
| query            | str  | The search term used to find company tickers            |         | True     |
| country          | str  | Search by country to find stocks matching the criteria  |         | True     |
| sector           | str  | Search by sector to find stocks matching the criteria   |         | True     |
| industry         | str  | Search by industry to find stocks matching the criteria |         | True     |
| exchange_country | str  | Search by exchange country to find stock matching       |         | True     |
| limit            | int  | The limit of companies shown.                           | 0       | True     |

---

## Returns

| Type         | Description    |
|--------------|----------------|
| pd.DataFrame | Search results |


---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.search(country="united states", exchange_country="Germany")
```

---
