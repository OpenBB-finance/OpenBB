---
title: tob
description: Get top of book bid and ask for any ticker on the CBOE exchange using
  the OpenBB Terminal. Default exchange is BZX, but can be changed to EDGX, BYX, or
  EDGA. Returns a Dataframe of Bids.
keywords:
- Top of Book bid
- Ask for ticker
- CBOE
- BZX
- EDGX
- BYX
- EDGA
- OpenBB Stocks
- Dataframe of Bids
- OpenBB finance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.tob - Reference | OpenBB SDK Docs" />

Get top of book bid and ask for ticker on exchange [CBOE.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/cboe_model.py#L12)]

```python
openbb.stocks.tob(symbol: str, exchange: str = "BZX")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get | None | False |
| exchange | str | Exchange to look at.  Can be `BZX`,`EDGX`, `BYX`, `EDGA` | BZX | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DatatFrame | Dataframe of Bids |
---
