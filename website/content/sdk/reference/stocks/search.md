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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L114)]

```python wordwrap
openbb.stocks.search(query: str = "", country: str = "", sector: str = "", industry_group: str = "", industry: str = "", exchange: str = "", exchange_country: str = "", all_exchanges: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| query | str | The search term used to find company tickers |  | True |
| country | str | Search by country to find stocks matching the criteria |  | True |
| sector | str | Search by sector to find stocks matching the criteria |  | True |
| industry_group | str | Search by industry group to find stocks matching the criteria |  | True |
| industry | str | Search by industry to find stocks matching the criteria |  | True |
| exchange | str | Search by exchange to find stock matching the criteria |  | True |
| exchange_country | str | Search by exchange country to find stock matching the criteria |  | True |
| all_exchanges | bool | Whether to search all exchanges, without this option only the United States market is searched | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of search results.<br/>Empty Dataframe if none are found. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.search(country="United States", exchange_country="Germany")
```

---

