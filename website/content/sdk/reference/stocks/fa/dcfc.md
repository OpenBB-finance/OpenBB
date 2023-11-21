---
title: dcfc
description: Get stocks dcf from FMP
keywords:
- stocks
- fa
- dcfc
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.dcfc - Reference | OpenBB SDK Docs" />

Get stocks dcf from FMP

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/fmp_model.py#L208)]

```python wordwrap
openbb.stocks.fa.dcfc(symbol: str, limit: int = 5, quarterly: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number to get | 5 | True |
| quarterly | bool | Flag to get quarterly data, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of dcf data |
---

