---
title: filter_stocks
description: This page provides an in-depth look into the function 'filter_stocks'
  used for filtering stocks based on various parameters like country, sector, industry,
  and market cap, and excluding specific exchanges. Understand the usage and benefits
  of this functionality in stock filtering.
keywords:
- filter stocks
- stock filters
- stock filtering
- finance database
- sector stocks
- industry stocks
- market cap
- stock exchange
- filter by country
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.sia.filter_stocks - Reference | OpenBB SDK Docs" />

Filter stocks based on country, sector, industry, market cap and exclude exchanges.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/sector_industry_analysis/financedatabase_model.py#L109)]

```python
openbb.stocks.sia.filter_stocks(country: str = None, sector: str = None, industry: str = None, marketcap: str = "", exclude_exchanges: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Search by country to find stocks matching the criteria. | None | True |
| sector | str | Search by sector to find stocks matching the criteria. | None | True |
| industry | str | Search by industry to find stocks matching the criteria. | None | True |
| marketcap | str | Select stocks based on the market cap. |  | True |
| exclude_exchanges | bool | When you wish to include different exchanges use this boolean. | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| list | List of filtered stocks |
---
