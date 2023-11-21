---
title: sec
description: Get SEC filings for a given stock ticker
keywords:
- stocks
- fa
- sec
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.sec - Reference | OpenBB SDK Docs" />

Get SEC filings for a given stock ticker. [Source: Nasdaq]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/nasdaq_model.py#L33)]

```python wordwrap
openbb.stocks.fa.sec(symbol: str, limit: int = 20, year: Optional[int] = None, form_group: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | The number of filings to return | 20 | True |
| year | Optional[int] | The year to grab from. The year will be ignored if form_group is not specified | None | True |
| form_group | Optional[str] | The form type to filter for:<br/>Choose from: annual, quarterly, proxies, insiders, 8-K, registrations, comments | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | SEC filings data |
---

