---
title: screen
description: Documentation for the ETF screen tool, a command-line Python application
  that scrapes and sorts data from stockanalysis.com. The tool offers various sorting
  options, including by assets, expense, and volume, among others.
keywords:
- ETF Screen
- Stock Analysis
- Data Scraping
- Github Repository
- CLI
- Parameters
- Sort
- Limit
- Reverse
- Financial Data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/screener/screen - Reference | OpenBB Terminal Docs" />

Screens ETFS from a personal scraping github repository. Data scraped from stockanalysis.com

### Usage

```python
screen [-l LIMIT] [-s {Assets,NAV,Expense,PE,SharesOut,Div,DivYield,Volume,Open,PrevClose,YrLow,YrHigh,Beta,N_Hold}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of etfs to display | 10 | True | None |
| sortby | Sort by given column. Default: Assets | Assets | True | Assets, NAV, Expense, PE, SharesOut, Div, DivYield, Volume, Open, PrevClose, YrLow, YrHigh, Beta, N_Hold |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |

---
