---
title: epsfc
description: Takes the ticker, asks for seekingalphaID and gets eps estimates
keywords:
- stocks
- fa
- epsfc
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.epsfc - Reference | OpenBB SDK Docs" />

Takes the ticker, asks for seekingalphaID and gets eps estimates

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/seeking_alpha_model.py#L16)]

```python wordwrap
openbb.stocks.fa.epsfc(ticker: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| ticker | str | ticker of company | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | eps estimates for the next 10yrs |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.fa.epsfc("AAPL")
```

---

