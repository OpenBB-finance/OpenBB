---
title: enterprise
description: This page provides detailed information about the financial modeling
  prep ticker enterprise, including python code, parameter descriptions, and returns.
keywords:
- Financial Modeling Prep Ticker Enterprise
- Enterprise Parameters
- Enterprise Returns
- Python code for Financial Modeling
- Fundamental Analysis Ticker Symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.enterprise - Reference | OpenBB SDK Docs" />

Financial Modeling Prep ticker enterprise

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L114)]

```python wordwrap
openbb.stocks.fa.enterprise(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, quarterly: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Fundamental analysis ticker symbol | None | False |
| start_date | str | Start date of data | None | True |
| end_date | str | End date of data | None | True |
| quarterly | bool | Flag to get quarterly data | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of enterprise information |
---

