---
title: eodchain
description: Get full EOD option date across all expirations
keywords:
- stocks
- options
- eodchain
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.eodchain - Reference | OpenBB SDK Docs" />

Get full EOD option date across all expirations

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/intrinio_model.py#L229)]

```python wordwrap
openbb.stocks.options.eodchain(symbol: str, date: str, quiet: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get option chain for | None | False |
| date | str | Date to get EOD chain for | None | False |
| quiet | bool | Flag to suppress progress bar | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of options across all expirations at a given close |
---

## Examples


To get the EOD chain for AAPL on Dec 23, 2022, we do the following

```python
from openbb_terminal.sdk import openbb
eod_chain = openbb.stocks.options.eodchain("AAPL", date="2022-12-23")
```

---

