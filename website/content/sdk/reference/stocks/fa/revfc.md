---
title: revfc
description: Takes the ticker, asks for seekingalphaID and gets rev estimates
keywords:
- stocks
- fa
- revfc
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.revfc - Reference | OpenBB SDK Docs" />

Takes the ticker, asks for seekingalphaID and gets rev estimates

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/seeking_alpha_model.py#L155)]

```python wordwrap
openbb.stocks.fa.revfc(ticker: str)
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
| pd.DataFrame | rev estimates for the next 10yrs |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.fa.revfc("AAPL")
```

---

