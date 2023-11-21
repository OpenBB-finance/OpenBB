---
title: compare
description: Compare selected ETFs
keywords:
- etf
- compare
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf.compare - Reference | OpenBB SDK Docs" />

Compare selected ETFs

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/etf/stockanalysis_model.py#L112)]

```python wordwrap
openbb.etf.compare(symbols: List[str])
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | ETF symbols to compare | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of etf comparisons |
---

## Examples

```python
from openbb_terminal.sdk import openbb
compare_etfs = openbb.etf.compare(["SPY", "QQQ", "IWM"])
```

---

