---
title: filings
description: Get SEC Filings RSS feed, disseminated by FMP
keywords:
- stocks
- disc
- filings
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.disc.filings - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get SEC Filings RSS feed, disseminated by FMP

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L760)]

```python wordwrap
openbb.stocks.disc.filings(pages: int = 1)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| pages | range = 1 | The range of most-rececnt pages to get entries from (1000 per page; maximum of 30 pages) | 1 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of results |
---

## Examples


df = openbb.stocks.filings()
df = openbb.stocks.filings(pages=30)

---



</TabItem>
<TabItem value="view" label="Chart">

Display recent forms submitted to the SEC

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/fmp_view.py#L19)]

```python wordwrap
openbb.stocks.disc.filings_chart(pages: int = 1, limit: int = 5, today: bool = False, export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| pages | int = 1 | The range of most-rececnt pages to get entries from (1000 per page, max 30 pages) | 1 | True |
| limit | int = 5 | Limit the number of entries to display (default: 5) | 5 | True |
| today | bool = False | Show all from today | False | True |
| export | str = "" | Export data as csv, json, or xlsx |  | True |


---

## Returns

This function does not return anything

---

## Examples


openbb.stocks.display_filings()
openbb.stocks.display_filings(today = True, export = "csv")

---



</TabItem>
</Tabs>